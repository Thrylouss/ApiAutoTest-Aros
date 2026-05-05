# api/test_users.py
from core.user import UserAPI


class TestUserProfile:
    def test_get_me_success(self, auth_client):
        # Просто вызываем метод, авторизация уже под капотом
        user_api = UserAPI(auth_client)
        response = user_api.get_me("/me/")

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "+998998987882"