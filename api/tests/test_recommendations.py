import pytest


class TestPlaces:
    latitude = 14.472913015051839
    longitude = 120.99698460538839
    user_message = "I'm looking for a cheap fast food restaurant"
    radius = 10000
    min_price = 1
    max_price = 3
    open_now = True
    category_ids = "63be6904847c3692a84b9bb5"
    limit = 5

    ai_recommendation = {
        "name": "Budget Bites",
        "reason": "Budget Bites offers affordable meals that are perfect for those looking for a quick and cheap dining option.",
    }

    fsq_places = [
        {
            "latitude": 14.12345678,
            "longitude": 120.12345678,
            "name": "Test Place",
            "location": {"formatted_address": "123 Test St, Test City"},
            "description": "A great place for fast food lovers.",
            "distance": 500,
            "price": 100,
            "rating": 3.5,
            "categories": [{"name": "Fast Food Restaurant"}],
        }
    ]

    @pytest.mark.asyncio
    async def test_places_with_one_limit(self, client, mocker):
        """Test the `/recommendations` endpoint with a limit of 1 and mocked dependencies."""

        async def mock_fetch_fsq_places(*args, **kwargs):
            return self.fsq_places

        def mock_chat_food_recommendations(*args, **kwargs):
            return self.ai_recommendation, []

        mocker.patch(
            "handler.restaurant_recommendations_handler.fetch_fsq_places",
            new=mock_fetch_fsq_places,
        )
        mocker.patch(
            "handler.ai_chat_recommendations_handler.chat_food_recommendations",
            new=mock_chat_food_recommendations,
        )

        response = client.get(
            f"/recommendations?latitude={self.latitude}&longitude={self.longitude}&user_message={self.user_message}&radius={self.radius}&min_price={self.min_price}&max_price={self.max_price}&open_now={self.open_now}&category_ids={self.category_ids}&limit={self.limit}"
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
        assert data["restaurants"][0]["latitude"] == 14.12345678
        assert data["restaurants"][0]["longitude"] == 120.12345678
        assert data["restaurants"][0]["name"] == "Test Place"
        assert data["restaurants"][0]["address"] == "123 Test St, Test City"
        assert (
            data["restaurants"][0]["description"]
            == "A great place for fast food lovers."
        )
        assert data["restaurants"][0]["distance"] == 500
        assert data["restaurants"][0]["price"] == 100
        assert data["restaurants"][0]["rating"] == 3.5

        # Test for the count of restaurants returned
        assert data["count"] == 1
