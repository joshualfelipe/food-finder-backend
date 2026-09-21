import json

from handler import ai_chat_handler

DEFAULT_FEATURES = ["radius_500.restaurant", "radius_500.cafe"]


class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)


class FakeResponse:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]


class TestResolveSearchParameters:
    def test_none_user_message_returns_default_without_calling_openai(self, mocker):
        mock_openai_conn = mocker.patch(
            "handler.ai_chat_handler.openai_service.openai_conn"
        )

        result = ai_chat_handler.resolve_search_parameters(None)

        assert result == DEFAULT_FEATURES
        mock_openai_conn.assert_not_called()

    def test_empty_user_message_returns_default_without_calling_openai(self, mocker):
        mock_openai_conn = mocker.patch(
            "handler.ai_chat_handler.openai_service.openai_conn"
        )

        result = ai_chat_handler.resolve_search_parameters("")

        assert result == DEFAULT_FEATURES
        mock_openai_conn.assert_not_called()

    def test_valid_json_filters_out_invalid_features(self, mocker):
        content = json.dumps({"features": ["walk_5.cafe", "not_a_real_feature"]})
        mocker.patch(
            "handler.ai_chat_handler.openai_service.openai_conn",
            return_value=FakeResponse(content),
        )

        result = ai_chat_handler.resolve_search_parameters("coffee nearby")

        assert result == ["walk_5.cafe"]

    def test_all_invalid_features_falls_back_to_default(self, mocker):
        content = json.dumps({"features": ["not_real", "also_not_real"]})
        mocker.patch(
            "handler.ai_chat_handler.openai_service.openai_conn",
            return_value=FakeResponse(content),
        )

        result = ai_chat_handler.resolve_search_parameters("coffee nearby")

        assert result == DEFAULT_FEATURES

    def test_malformed_json_falls_back_to_default(self, mocker):
        mocker.patch(
            "handler.ai_chat_handler.openai_service.openai_conn",
            return_value=FakeResponse("not valid json"),
        )

        result = ai_chat_handler.resolve_search_parameters("coffee nearby")

        assert result == DEFAULT_FEATURES

    def test_none_content_falls_back_to_default(self, mocker):
        mocker.patch(
            "handler.ai_chat_handler.openai_service.openai_conn",
            return_value=FakeResponse(None),
        )

        result = ai_chat_handler.resolve_search_parameters("coffee nearby")

        assert result == DEFAULT_FEATURES
