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
