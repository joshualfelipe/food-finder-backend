import json
from types import SimpleNamespace

from fastapi.testclient import TestClient
from handler import restaurant_recommendations_handler
from main import app
import httpx
import pytest


def _feature(name, lat, lon, cuisine="mixed", categories=None, takeaway=None):
    return {
        "properties": {
            "name": name,
            "lat": lat,
            "lon": lon,
            "catering": {"cuisine": cuisine} if cuisine is not None else {},
            "categories": categories or ["catering.restaurant"],
            "facilities": {"takeaway": takeaway} if takeaway is not None else {},
        }
    }


def _thread(thread_id="thread-123"):
    return SimpleNamespace(thread_id=thread_id)


class TestPlaces:
    latitude = 14.472913015051839
    longitude = 120.99698460538839
    user_message = "I'm looking for a cheap fast food restaurant"

    ai_response = {
        "recommendations": [
            {
                "name": "Budget Bites",
                "reason": "Budget Bites offers affordable meals that are perfect for those looking for a quick and cheap dining option.",
            }
        ],
        "summary": "Found a solid, cheap fast food spot close by.",
    }

    def _mock_conversation_handler(self, mocker, thread_id="thread-123"):
        return mocker.patch(
            "handler.restaurant_recommendations_handler.conversation_handler.create_message",
            return_value=_thread(thread_id),
        )

    def _mock_ai_recommendations(self, mocker, response=None):
        return mocker.patch(
            "handler.restaurant_recommendations_handler.ai_recommendations_handler.chat_food_recommendations",
            return_value=response if response is not None else self.ai_response,
        )

    def _url(self, **overrides):
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "user_message": self.user_message,
        }
        params.update(overrides)
        query = "&".join(f"{key}={value}" for key, value in params.items() if value is not None)
        return f"/recommendations?{query}"

    @pytest.mark.asyncio
    async def test_places_with_one_result(self, client, mocker):
        """Test the `/recommendations` endpoint with mocked dependencies."""

        class MockGeoapifyResponse:
            def json(self):
                return {
                    "features": [
                        _feature(
                            "Budget Bites",
                            14.4735,
                            120.9975,
                            cuisine="burger",
                            takeaway=True,
                        ),
                    ]
                }

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        self._mock_conversation_handler(mocker)
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        self._mock_ai_recommendations(mocker)

        response = client.get(self._url())

        assert response.status_code == 200
        data = response.json()

        assert data["thread_id"] == "thread-123"
        assert data["summary"] == self.ai_response["summary"]
        assert data["ai_recommendations"] == {
            "recommendations": self.ai_response["recommendations"]
        }

        assert data["restaurants"][0]["name"] == "Budget Bites"
        assert data["restaurants"][0]["catering_cuisine"] == "burger"
        assert data["restaurants"][0]["latitude"] == 14.4735
        assert data["restaurants"][0]["longitude"] == 120.9975
        assert data["restaurants"][0]["distance_m"] > 0
        assert "categories" not in data["restaurants"][0]
        assert "facilities_takeaway" not in data["restaurants"][0]

        assert data["count"] == 1

    @pytest.mark.asyncio
    async def test_places_with_multiple_results(self, client, mocker):
        class MockGeoapifyResponse:
            def json(self):
                return {
                    "features": [
                        _feature("Budget Bites", 14.4735, 120.9975, cuisine="burger", takeaway=True),
                        _feature("Second Spot", 14.474, 120.998, cuisine="pizza", takeaway=False),
                        _feature(
                            "Third Place",
                            14.475,
                            120.999,
                            cuisine="coffee",
                            categories=["catering.cafe"],
                            takeaway=True,
                        ),
                    ]
                }

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        self._mock_conversation_handler(mocker)
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        self._mock_ai_recommendations(mocker)

        response = client.get(self._url())

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 3
        names = [r["name"] for r in data["restaurants"]]
        assert names == ["Budget Bites", "Second Spot", "Third Place"]
        assert all(r["distance_m"] > 0 for r in data["restaurants"])

    @pytest.mark.asyncio
    async def test_places_skips_entries_missing_name(self, client, mocker):
        class MockGeoapifyResponse:
            def json(self):
                return {
                    "features": [
                        {
                            "properties": {
                                "lat": 14.4735,
                                "lon": 120.9975,
                                "catering": {"cuisine": "burger"},
                            }
                        },
                        _feature("Budget Bites", 14.474, 120.998, cuisine="burger", takeaway=True),
                    ]
                }

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        self._mock_conversation_handler(mocker)
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        self._mock_ai_recommendations(mocker)

        response = client.get(self._url())

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 1
        assert data["restaurants"][0]["name"] == "Budget Bites"

    @pytest.mark.asyncio
    async def test_places_deduplicates_by_name(self, client, mocker):
        class MockGeoapifyResponse:
            def json(self):
                return {
                    "features": [
                        _feature("Budget Bites", 14.4735, 120.9975, cuisine="burger"),
                        _feature("Budget Bites", 14.5, 121.02, cuisine="burger"),
                    ]
                }

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        self._mock_conversation_handler(mocker)
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        self._mock_ai_recommendations(mocker)

        response = client.get(self._url())

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 1
        assert data["restaurants"][0]["latitude"] == 14.4735

    @pytest.mark.asyncio
    async def test_places_with_only_origin_point_returns_zero_count(self, client, mocker):
        class MockGeoapifyResponse:
            def json(self):
                return {"features": []}

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        self._mock_conversation_handler(mocker)
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        self._mock_ai_recommendations(mocker)

        response = client.get(self._url())

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 0
        assert data["restaurants"] == []

    @pytest.mark.asyncio
    async def test_places_missing_features_key_returns_zero_count(self, client, mocker):
        class MockGeoapifyResponse:
            def json(self):
                return {}

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        self._mock_conversation_handler(mocker)
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        self._mock_ai_recommendations(mocker)

        response = client.get(self._url())

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 0
        assert data["restaurants"] == []

    @pytest.mark.asyncio
    async def test_places_missing_catering_and_facilities_returns_none_fields(self, client, mocker):
        class MockGeoapifyResponse:
            def json(self):
                return {
                    "features": [
                        {
                            "properties": {
                                "name": "No Extras Diner",
                                "lat": 14.4735,
                                "lon": 120.9975,
                                "categories": ["catering.restaurant"],
                            }
                        },
                    ]
                }

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        self._mock_conversation_handler(mocker)
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        self._mock_ai_recommendations(mocker)

        response = client.get(self._url())

        assert response.status_code == 200
        data = response.json()

        assert data["restaurants"][0]["catering_cuisine"] is None

    @pytest.mark.asyncio
    async def test_geoapify_queried_with_fixed_categories_regardless_of_message(self, client, mocker):
        class MockGeoapifyResponse:
            def json(self):
                return {"features": []}

        captured = {}

        async def mock_geoapify_conn(params):
            captured["params"] = params
            return MockGeoapifyResponse()

        self._mock_conversation_handler(mocker)
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        self._mock_ai_recommendations(mocker)

        response = client.get(
            self._url(user_message="surprise me with something exotic")
        )

        assert response.status_code == 200
        assert captured["params"].categories == restaurant_recommendations_handler.PLACE_CATEGORIES

    @pytest.mark.asyncio
    async def test_ai_candidates_are_capped_to_nearest_max_and_sorted(self, client, mocker):
        max_candidates = restaurant_recommendations_handler.MAX_AI_CANDIDATES
        total = max_candidates + 5
        features = [
            _feature(f"Restaurant {i}", self.latitude, self.longitude + (i + 1) * 0.001)
            for i in range(total)
        ]

        class MockGeoapifyResponse:
            def json(self):
                return {"features": features}

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        self._mock_conversation_handler(mocker)
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        mock_chat = self._mock_ai_recommendations(mocker)

        response = client.get(self._url())

        assert response.status_code == 200
        assert response.json()["count"] == total

        ai_restaurant_data = mock_chat.call_args[0][0]
        assert len(ai_restaurant_data) == max_candidates

        distances = [r["distance_m"] for r in ai_restaurant_data]
        assert distances == sorted(distances)
        assert set(ai_restaurant_data[0].keys()) == set(
            restaurant_recommendations_handler.AI_VISIBLE_FIELDS
        )

    @pytest.mark.asyncio
    async def test_conversation_history_is_fetched_when_thread_id_provided(self, client, mocker):
        class MockGeoapifyResponse:
            def json(self):
                return {"features": []}

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        self._mock_conversation_handler(mocker, thread_id="thread-abc")
        mock_get_messages = mocker.patch(
            "handler.restaurant_recommendations_handler.conversation_handler.get_messages",
            return_value=[],
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        self._mock_ai_recommendations(mocker)

        response = client.get(self._url(thread_id="thread-abc"))

        assert response.status_code == 200
        mock_get_messages.assert_called_once_with("thread-abc", "test-user-id")

    @pytest.mark.asyncio
    async def test_conversation_history_not_fetched_without_thread_id(self, client, mocker):
        class MockGeoapifyResponse:
            def json(self):
                return {"features": []}

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        self._mock_conversation_handler(mocker)
        mock_get_messages = mocker.patch(
            "handler.restaurant_recommendations_handler.conversation_handler.get_messages",
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        self._mock_ai_recommendations(mocker)

        response = client.get(self._url())

        assert response.status_code == 200
        mock_get_messages.assert_not_called()

    @pytest.mark.asyncio
    async def test_bot_reply_is_saved_to_conversation_with_summary(self, client, mocker):
        class MockGeoapifyResponse:
            def json(self):
                return {"features": []}

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        mock_create_message = self._mock_conversation_handler(mocker, thread_id="thread-xyz")
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        self._mock_ai_recommendations(mocker)

        response = client.get(self._url())

        assert response.status_code == 200
        assert mock_create_message.call_count == 2

        bot_message = mock_create_message.call_args_list[1][0][0]
        assert bot_message.role == "bot"
        assert bot_message.thread_id == "thread-xyz"
        recommended = json.dumps(self.ai_response["recommendations"], ensure_ascii=False)
        assert bot_message.content == f"{self.ai_response['summary']}\nRecommended: {recommended}"

    @pytest.mark.asyncio
    async def test_no_match_ai_response_still_populates_summary(self, client, mocker):
        class MockGeoapifyResponse:
            def json(self):
                return {"features": []}

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        self._mock_conversation_handler(mocker)
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        self._mock_ai_recommendations(
            mocker,
            response={
                "error": "no_match",
                "message": "Nothing nearby fits that well right now — want me to broaden the search?",
            },
        )

        response = client.get(self._url())

        assert response.status_code == 200
        data = response.json()

        assert data["summary"] == "Nothing nearby fits that well right now — want me to broaden the search?"
        assert data["ai_recommendations"] == {"error": "no_match"}

    def test_places_missing_query_params_returns_422(self, client):
        response = client.get("/recommendations")

        assert response.status_code == 422

    def test_places_geoapify_error_returns_500(self, mocker):
        async def mock_geoapify_conn_raises(*args, **kwargs):
            raise httpx.ConnectTimeout("boom")

        self._mock_conversation_handler(mocker)
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn_raises,
        )

        local_client = TestClient(app, raise_server_exceptions=False)
        response = local_client.get(self._url())

        assert response.status_code == 500
