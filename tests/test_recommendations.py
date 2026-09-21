from fastapi.testclient import TestClient
from main import app
import httpx
import pytest


class TestPlaces:
    latitude = 14.472913015051839
    longitude = 120.99698460538839
    user_message = "I'm looking for a cheap fast food restaurant"

    ai_recommendation = {
        "name": "Budget Bites",
        "reason": "Budget Bites offers affordable meals that are perfect for those looking for a quick and cheap dining option.",
    }

    @pytest.mark.asyncio
    async def test_places_with_one_result(self, client, mocker):
        """Test the `/recommendations` endpoint with mocked dependencies."""

        class MockGeoapifyResponse:
            def json(self):
                return {
                    "features": [
                        {"properties": {"name": "Origin Point"}},
                        {
                            "properties": {
                                "name": "Budget Bites",
                                "lat": 14.4735,
                                "lon": 120.9975,
                                "catering": {"cuisine": "burger"},
                                "categories": ["catering.restaurant"],
                                "facilities": {"takeaway": True},
                            }
                        },
                    ]
                }

        def mock_resolve_search_parameters(*args, **kwargs):
            return ["catering.restaurant"]

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        def mock_chat_food_recommendations(*args, **kwargs):
            return self.ai_recommendation, []

        mocker.patch(
            "handler.restaurant_recommendations_handler.ai_chat_handler.resolve_search_parameters",
            new=mock_resolve_search_parameters,
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.ai_recommendations_handler.chat_food_recommendations",
            new=mock_chat_food_recommendations,
        )

        response = client.get(
            f"/recommendations?latitude={self.latitude}&longitude={self.longitude}&user_message={self.user_message}"
        )

        assert response.status_code == 200
        data = response.json()

        # Test for the AI recommendation content
        assert data["ai_recommendations"]["name"] == "Budget Bites"
        assert (
            data["ai_recommendations"]["reason"]
            == "Budget Bites offers affordable meals that are perfect for those looking for a quick and cheap dining option."
        )

        # Test for the restaurant details returned
        assert data["restaurants"][0]["name"] == "Budget Bites"
        assert data["restaurants"][0]["catering_cuisine"] == "burger"
        assert data["restaurants"][0]["categories"] == ["catering.restaurant"]
        assert data["restaurants"][0]["facilities_takeaway"] is True
        assert data["restaurants"][0]["distance_m"] > 0

        # Test for the count of restaurants returned
        assert data["count"] == 1

    @pytest.mark.asyncio
    async def test_places_with_multiple_results(self, client, mocker):
        class MockGeoapifyResponse:
            def json(self):
                return {
                    "features": [
                        {"properties": {"name": "Origin Point"}},
                        {
                            "properties": {
                                "name": "Budget Bites",
                                "lat": 14.4735,
                                "lon": 120.9975,
                                "catering": {"cuisine": "burger"},
                                "categories": ["catering.restaurant"],
                                "facilities": {"takeaway": True},
                            }
                        },
                        {
                            "properties": {
                                "name": "Second Spot",
                                "lat": 14.474,
                                "lon": 120.998,
                                "catering": {"cuisine": "pizza"},
                                "categories": ["catering.restaurant"],
                                "facilities": {"takeaway": False},
                            }
                        },
                        {
                            "properties": {
                                "name": "Third Place",
                                "lat": 14.475,
                                "lon": 120.999,
                                "catering": {"cuisine": "coffee"},
                                "categories": ["catering.cafe"],
                                "facilities": {"takeaway": True},
                            }
                        },
                    ]
                }

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        def mock_chat_food_recommendations(*args, **kwargs):
            return self.ai_recommendation, []

        mocker.patch(
            "handler.restaurant_recommendations_handler.ai_chat_handler.resolve_search_parameters",
            return_value=["catering.restaurant"],
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.ai_recommendations_handler.chat_food_recommendations",
            new=mock_chat_food_recommendations,
        )

        response = client.get(
            f"/recommendations?latitude={self.latitude}&longitude={self.longitude}&user_message={self.user_message}"
        )

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
                        {"properties": {"name": "Origin Point"}},
                        {
                            "properties": {
                                "lat": 14.4735,
                                "lon": 120.9975,
                                "catering": {"cuisine": "burger"},
                            }
                        },
                        {
                            "properties": {
                                "name": "Budget Bites",
                                "lat": 14.474,
                                "lon": 120.998,
                                "catering": {"cuisine": "burger"},
                                "categories": ["catering.restaurant"],
                                "facilities": {"takeaway": True},
                            }
                        },
                    ]
                }

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        def mock_chat_food_recommendations(*args, **kwargs):
            return self.ai_recommendation, []

        mocker.patch(
            "handler.restaurant_recommendations_handler.ai_chat_handler.resolve_search_parameters",
            return_value=["catering.restaurant"],
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.ai_recommendations_handler.chat_food_recommendations",
            new=mock_chat_food_recommendations,
        )

        response = client.get(
            f"/recommendations?latitude={self.latitude}&longitude={self.longitude}&user_message={self.user_message}"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 1
        assert data["restaurants"][0]["name"] == "Budget Bites"

    @pytest.mark.asyncio
    async def test_places_with_only_origin_point_returns_zero_count(self, client, mocker):
        class MockGeoapifyResponse:
            def json(self):
                return {"features": [{"properties": {"name": "Origin Point"}}]}

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        def mock_chat_food_recommendations(*args, **kwargs):
            return self.ai_recommendation, []

        mocker.patch(
            "handler.restaurant_recommendations_handler.ai_chat_handler.resolve_search_parameters",
            return_value=["catering.restaurant"],
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.ai_recommendations_handler.chat_food_recommendations",
            new=mock_chat_food_recommendations,
        )

        response = client.get(
            f"/recommendations?latitude={self.latitude}&longitude={self.longitude}&user_message={self.user_message}"
        )

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

        def mock_chat_food_recommendations(*args, **kwargs):
            return self.ai_recommendation, []

        mocker.patch(
            "handler.restaurant_recommendations_handler.ai_chat_handler.resolve_search_parameters",
            return_value=["catering.restaurant"],
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.ai_recommendations_handler.chat_food_recommendations",
            new=mock_chat_food_recommendations,
        )

        response = client.get(
            f"/recommendations?latitude={self.latitude}&longitude={self.longitude}&user_message={self.user_message}"
        )

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
                        {"properties": {"name": "Origin Point"}},
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

        def mock_chat_food_recommendations(*args, **kwargs):
            return self.ai_recommendation, []

        mocker.patch(
            "handler.restaurant_recommendations_handler.ai_chat_handler.resolve_search_parameters",
            return_value=["catering.restaurant"],
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.ai_recommendations_handler.chat_food_recommendations",
            new=mock_chat_food_recommendations,
        )

        response = client.get(
            f"/recommendations?latitude={self.latitude}&longitude={self.longitude}&user_message={self.user_message}"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["restaurants"][0]["catering_cuisine"] is None
        assert data["restaurants"][0]["facilities_takeaway"] is None

    @pytest.mark.asyncio
    async def test_places_without_user_message_skips_openai_parameter_matching(self, client, mocker):
        class MockGeoapifyResponse:
            def json(self):
                return {"features": [{"properties": {"name": "Origin Point"}}]}

        async def mock_geoapify_conn(*args, **kwargs):
            return MockGeoapifyResponse()

        mock_openai_conn = mocker.patch("handler.ai_chat_handler.openai_service.openai_conn")

        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn,
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.ai_recommendations_handler.chat_food_recommendations",
            return_value=(self.ai_recommendation, []),
        )

        response = client.get(
            f"/recommendations?latitude={self.latitude}&longitude={self.longitude}"
        )

        assert response.status_code == 200
        mock_openai_conn.assert_not_called()

    def test_places_missing_query_params_returns_422(self, client):
        response = client.get("/recommendations")

        assert response.status_code == 422

    def test_places_geoapify_error_returns_500(self, mocker):
        async def mock_geoapify_conn_raises(*args, **kwargs):
            raise httpx.ConnectTimeout("boom")

        mocker.patch(
            "handler.restaurant_recommendations_handler.ai_chat_handler.resolve_search_parameters",
            return_value=["catering.restaurant"],
        )
        mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn",
            new=mock_geoapify_conn_raises,
        )

        local_client = TestClient(app, raise_server_exceptions=False)
        response = local_client.get(
            f"/recommendations?latitude={self.latitude}&longitude={self.longitude}&user_message={self.user_message}"
        )

        assert response.status_code == 500
