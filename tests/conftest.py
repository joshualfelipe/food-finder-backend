from controller.auth_controller import get_current_user
from dto.auth_dto import MeResponseDTO
from fastapi.testclient import TestClient
from main import app
import pytest


def _fake_current_user() -> MeResponseDTO:
    return MeResponseDTO(
        user_id="test-user-id",
        email="test@example.com",
        display_name="Test User",
        created_at="2024-01-01T00:00:00Z",
    )


app.dependency_overrides[get_current_user] = _fake_current_user


@pytest.fixture
def client():
    return TestClient(app)
