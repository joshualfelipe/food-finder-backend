from datetime import datetime, timezone
import uuid

from dto.conversation_dto import ConversationResponse
from fastapi.testclient import TestClient
from main import app
from postgrest.exceptions import APIError
import pytest

OWNER_ID = "test-user-id"
OTHER_USER_ID = "other-user-id"
THREAD_ID = "thread-123"


def _thread(user_id):
    return ConversationResponse(
        thread_id=THREAD_ID,
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
        updated_at=None,
        deleted_at=None,
    )


def _message_row(thread_id=THREAD_ID, role="user", content="hello"):
    return {
        "thread_id": thread_id,
        "role": role,
        "content": content,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "deleted_at": None,
    }


@pytest.fixture
def mock_repo(mocker):
    base = "handler.conversation_handler.conversation_repository"

    class Repo:
        get_thread = mocker.patch(f"{base}.get_thread")
        get_messages_from_thread = mocker.patch(
            f"{base}.get_messages_from_thread", return_value=[]
        )
        save_message = mocker.patch(f"{base}.save_message")
        create_new_thread = mocker.patch(f"{base}.create_new_thread", return_value="new-thread")

    return Repo


class TestGetMessages:
    def test_returns_404_when_thread_not_found(self, client, mock_repo):
        mock_repo.get_thread.return_value = None

        response = client.get(f"/get_messages?thread_id={THREAD_ID}")

        assert response.status_code == 404
        mock_repo.get_messages_from_thread.assert_not_called()

    def test_returns_403_when_thread_owned_by_another_user(self, client, mock_repo):
        mock_repo.get_thread.return_value = _thread(OTHER_USER_ID)

        response = client.get(f"/get_messages?thread_id={THREAD_ID}")

        assert response.status_code == 403
        mock_repo.get_messages_from_thread.assert_not_called()

    def test_owner_can_read_messages(self, client, mock_repo):
        mock_repo.get_thread.return_value = _thread(OWNER_ID)

        response = client.get(f"/get_messages?thread_id={THREAD_ID}")

        assert response.status_code == 200
        mock_repo.get_messages_from_thread.assert_called_once_with(THREAD_ID, None)


class TestSendMessage:
    def test_returns_404_when_thread_not_found(self, client, mock_repo):
        mock_repo.get_thread.return_value = None

        response = client.post(
            "/send_message", json={"thread_id": THREAD_ID, "role": None, "content": "hi"}
        )

        assert response.status_code == 404
        mock_repo.save_message.assert_not_called()

    def test_returns_403_when_thread_owned_by_another_user(self, client, mock_repo):
        mock_repo.get_thread.return_value = _thread(OTHER_USER_ID)

        response = client.post(
            "/send_message", json={"thread_id": THREAD_ID, "role": None, "content": "hi"}
        )

        assert response.status_code == 403
        mock_repo.save_message.assert_not_called()

    def test_owner_can_send_message(self, client, mock_repo):
        mock_repo.get_thread.return_value = _thread(OWNER_ID)
        mock_repo.save_message.return_value = _message_row(content="hi")

        response = client.post(
            "/send_message", json={"thread_id": THREAD_ID, "role": None, "content": "hi"}
        )

        assert response.status_code == 200
        mock_repo.save_message.assert_called_once()

    def test_new_thread_skips_ownership_check(self, client, mock_repo):
        mock_repo.save_message.return_value = _message_row(thread_id="new-thread", content="hi")

        response = client.post(
            "/send_message", json={"thread_id": None, "role": None, "content": "hi"}
        )

        assert response.status_code == 200
        mock_repo.get_thread.assert_not_called()
        mock_repo.create_new_thread.assert_called_once_with(OWNER_ID)


class TestRecommendationsThreadOwnership:
    url = "/recommendations?latitude=14.47&longitude=120.99&user_message=food&thread_id=" + THREAD_ID

    @pytest.fixture
    def mock_geoapify(self, mocker):
        return mocker.patch(
            "handler.restaurant_recommendations_handler.geoapify_service.geoapify_conn"
        )

    def test_returns_404_when_thread_not_found(self, client, mock_repo, mock_geoapify):
        mock_repo.get_thread.return_value = None

        response = client.get(self.url)

        assert response.status_code == 404
        mock_repo.save_message.assert_not_called()
        mock_geoapify.assert_not_called()

    def test_returns_403_when_thread_owned_by_another_user(
        self, client, mock_repo, mock_geoapify
    ):
        mock_repo.get_thread.return_value = _thread(OTHER_USER_ID)

        response = client.get(self.url)

        assert response.status_code == 403
        mock_repo.get_messages_from_thread.assert_not_called()
        mock_repo.save_message.assert_not_called()
        mock_geoapify.assert_not_called()


class TestDatabaseErrors:
    def _raise(self, mock_repo, code):
        mock_repo.get_thread.side_effect = APIError(
            {"code": code, "message": "permission denied for table threads", "hint": "GRANT ..."}
        )

    def test_permission_denied_returns_500_without_leaking_details(self, mock_repo, caplog):
        self._raise(mock_repo, "42501")
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get(f"/get_messages?thread_id={THREAD_ID}")

        assert response.status_code == 500
        body = response.json()
        assert body["detail"] == "A database error occurred."
        assert "threads" not in response.text

        # error_id is a valid uuid and appears in the log line with the full DB details
        uuid.UUID(body["error_id"])
        assert body["error_id"] in caplog.text
        assert "42501" in caplog.text

    def test_unique_violation_returns_409(self, client, mock_repo):
        self._raise(mock_repo, "23505")

        response = client.get(f"/get_messages?thread_id={THREAD_ID}")

        assert response.status_code == 409
