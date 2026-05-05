# utils/client.py

class ProductAPI:
    def __init__(self, client):
        self.client = client

    def get_product(self, endpoint):
        """Токен подставится автоматически из настроек клиента"""
        return self.client.get(f"/v1/product{endpoint}")