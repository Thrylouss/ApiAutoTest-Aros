# api/product/test_category_list.py
from core.product import ProductAPI


class TestProduct:
    def test_get_category_list_success(self, auth_client):
        # Просто вызываем метод, авторизация уже под капотом
        product_api = ProductAPI(auth_client)
        response = product_api.get_product("/category_list/")

        assert response.status_code == 200