import pytest


class TestPlaces:
    latitude = 14.472913015051839
    longitude = 120.99698460538839

    @pytest.mark.asyncio
    async def test_places_with_one_limit(self, client, mocker):

        fake_response = {
            "results": [
                {
                    "latitude": 14.47,
                    "longitude": 120.99,
                    "name": "Test Place",
                    "location": {"formatted_address": "Test Address"},
                    "description": "Nice place",
                    "distance": 100,
                    "price": 2,
                    "rating": 4.5,
                }
            ]
        }

        # Mock httpx.AsyncClient.get
        async def mock_get(*args, **kwargs):
            class MockResponse:
                def json(self):
                    return fake_response

            return MockResponse()

        mocker.patch("httpx.AsyncClient.get", mock_get)

        response = client.get(
            f"/places?latitude={self.latitude}&longitude={self.longitude}"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["count"] == 1
        assert data["places"][0]["name"] == "Test Place"
