import json
from types import SimpleNamespace

from handler import ai_recommendations_handler


class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)


class FakeResponse:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]


def _message(content="cheap food"):
    return SimpleNamespace(role="user", content=content)


class TestChatFoodRecommendations:
    def test_valid_json_response_is_parsed(self, mocker):
        content = json.dumps(
            {
                "recommendations": [{"name": "Budget Bites", "reason": "cheap"}],
                "summary": "Found a cheap spot nearby.",
            }
        )
        mocker.patch(
            "handler.ai_recommendations_handler.openai_service.openai_conn",
            return_value=FakeResponse(content),
        )

        result = ai_recommendations_handler.chat_food_recommendations(
            [], [], _message()
        )

        assert result == {
            "recommendations": [{"name": "Budget Bites", "reason": "cheap"}],
            "summary": "Found a cheap spot nearby.",
        }

    def test_invalid_json_response_returns_error_payload(self, mocker):
        mocker.patch(
            "handler.ai_recommendations_handler.openai_service.openai_conn",
            return_value=FakeResponse("not valid json"),
        )

        result = ai_recommendations_handler.chat_food_recommendations(
            [], [], _message()
        )

        assert result == {"error": "invalid_ai_json", "raw": "not valid json"}

    def test_none_content_defaults_to_empty_object(self, mocker):
        mocker.patch(
            "handler.ai_recommendations_handler.openai_service.openai_conn",
            return_value=FakeResponse(None),
        )

        result = ai_recommendations_handler.chat_food_recommendations(
            [], [], _message()
        )

        assert result == {}

    def test_sends_expected_openai_request_shape(self, mocker):
        mock_openai_conn = mocker.patch(
            "handler.ai_recommendations_handler.openai_service.openai_conn",
            return_value=FakeResponse("{}"),
        )

        ai_recommendations_handler.chat_food_recommendations(
            [{"name": "Budget Bites"}], [], _message("cheap food")
        )

        params = mock_openai_conn.call_args[0][0]
        assert params.max_completion_tokens == 600
        assert params.temperature == 0.3
        assert params.messages[0].role == "developer"
        assert params.messages[-1].role == "user"
        assert "cheap food" in params.messages[-1].content
        assert "Budget Bites" in params.messages[-1].content


class TestExtractChatText:
    def test_returns_summary_when_present(self):
        result = ai_recommendations_handler.extract_chat_text(
            {"recommendations": [], "summary": "Great picks nearby."}
        )

        assert result == "Great picks nearby."

    def test_falls_back_to_message_when_no_summary(self):
        result = ai_recommendations_handler.extract_chat_text(
            {"error": "no_match", "message": "Nothing fits right now."}
        )

        assert result == "Nothing fits right now."

    def test_empty_summary_falls_back_to_message(self):
        result = ai_recommendations_handler.extract_chat_text(
            {"summary": "", "message": "fallback text"}
        )

        assert result == "fallback text"

    def test_falls_back_to_json_dump_when_neither_present(self):
        payload = {"error": "invalid_ai_json", "raw": "garbage"}

        result = ai_recommendations_handler.extract_chat_text(payload)

        assert result == json.dumps(payload)

    def test_non_dict_input_returns_json_dump(self):
        result = ai_recommendations_handler.extract_chat_text(["unexpected"])

        assert result == json.dumps(["unexpected"])


class TestFormatConversationHistory:
    def test_none_history_returns_empty_list(self):
        assert ai_recommendations_handler.format_conversation_history(None) == []

    def test_history_longer_than_six_is_truncated_to_last_six(self):
        history = [SimpleNamespace(role="user", content=str(i)) for i in range(10)]

        result = ai_recommendations_handler.format_conversation_history(history)

        assert len(result) == 6
        assert [item["content"] for item in result] == [str(i) for i in range(4, 10)]

    def test_user_role_is_preserved(self):
        history = [SimpleNamespace(role="user", content="hi")]

        result = ai_recommendations_handler.format_conversation_history(history)

        assert result == [{"role": "user", "content": "hi"}]

    def test_non_user_role_is_mapped_to_assistant(self):
        history = [SimpleNamespace(role="bot", content="hello there")]

        result = ai_recommendations_handler.format_conversation_history(history)

        assert result == [{"role": "assistant", "content": "hello there"}]


class TestFormatAiChatPrompt:
    def test_builds_expected_message_sequence(self):
        restaurant_data = [{"name": "Budget Bites"}]
        formatted_history = [{"role": "user", "content": "earlier question"}]
        message = _message("cheap food nearby")

        result = ai_recommendations_handler.format_ai_chat_prompt(
            restaurant_data, formatted_history, message
        )

        assert result[0]["role"] == "developer"
        assert result[1] == {"role": "user", "content": "earlier question"}
        assert result[2]["role"] == "user"
        assert "cheap food nearby" in result[2]["content"]
        assert "Budget Bites" in result[2]["content"]
