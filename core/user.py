# utils/client.py

class UserAPI:
    def __init__(self, client):
        self.client = client

    def get_me(self, endpoint):
        """Токен подставится автоматически из настроек клиента"""
        return self.client.get(f"/v1/user{endpoint}")