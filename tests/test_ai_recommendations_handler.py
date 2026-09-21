import json

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


class TestChatFoodRecommendations:
    def test_valid_json_response_is_parsed(self, mocker):
        content = json.dumps(
            {"recommendations": [{"name": "Budget Bites", "reason": "cheap"}]}
        )
        mocker.patch(
            "handler.ai_recommendations_handler.openai_service.openai_conn",
            return_value=FakeResponse(content),
        )

        result, _ = ai_recommendations_handler.chat_food_recommendations(
            "cheap food", []
        )

        assert result == {
            "recommendations": [{"name": "Budget Bites", "reason": "cheap"}]
        }

    def test_invalid_json_response_returns_error_payload(self, mocker):
        mocker.patch(
            "handler.ai_recommendations_handler.openai_service.openai_conn",
            return_value=FakeResponse("not valid json"),
        )

        result, _ = ai_recommendations_handler.chat_food_recommendations(
            "cheap food", []
        )

        assert result == {"error": "invalid_ai_json", "raw": "not valid json"}

    def test_none_content_defaults_to_empty_object(self, mocker):
        mocker.patch(
            "handler.ai_recommendations_handler.openai_service.openai_conn",
            return_value=FakeResponse(None),
        )

        result, _ = ai_recommendations_handler.chat_food_recommendations(
            "cheap food", []
        )

        assert result == {}


class TestFormatConversationHistory:
    def test_none_history_returns_empty_list(self):
        assert ai_recommendations_handler.format_conversation_history(None) == []

    def test_history_longer_than_six_is_truncated_to_last_six(self):
        history = [{"role": "user", "content": str(i)} for i in range(10)]

        result = ai_recommendations_handler.format_conversation_history(history)

        assert result == history[-6:]
