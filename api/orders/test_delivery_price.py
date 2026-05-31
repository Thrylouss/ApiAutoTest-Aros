import pytest
import allure
from core.orders import OrdersAPI

@allure.epic("Orders")
@allure.feature("Delivery Price Calculation")
class TestDeliveryPrice:
    """Тесты для POST /web/v2/orders/calculate_delivery_price/"""

    @pytest.fixture(scope="class")
    def api(self, auth_client):
        return OrdersAPI(auth_client)

    @allure.title("Успешный расчет стоимости доставки")
    def test_calculate_success(self, api):
        payload = {
            "delivery_method": 2, # Например, "В офис Ароса"
            "receiver_city": 3,
            "order_products": [{"product_variant": 2348, "quantity": 1}]
        }
        r = api.calculate_delivery_price(**payload)
        assert r.status_code == 200
        data = r.json()
        assert "delivery_price" in data
        assert float(data["delivery_price"]) >= 0 # Цена не может быть отрицательной

    @allure.title("Проверка бесплатной доставки (для офиса)")
    def test_office_delivery_is_free(self, api):
        # Метод доставки 2 (офис Арос) обычно бесплатен
        payload = {
            "delivery_method": 2,
            "receiver_city": 3,
            "order_products": [{"product_variant": 2348, "quantity": 1}]
        }
        r = api.calculate_delivery_price(**payload)
        assert float(r.json()["delivery_price"]) == 0.0

    @allure.title("Расчет для нескольких товаров")
    def test_calculate_multiple_products(self, api):
        payload = {
            "delivery_method": 1, # "Aros до адресу" (обычно платно)
            "receiver_city": 3,
            "order_products": [
                {"product_variant": 2348, "quantity": 1},
                {"product_variant": 2348, "quantity": 2}
            ]
        }
        r = api.calculate_delivery_price(**payload)
        assert r.status_code == 200
        # Стоимость доставки может вырасти при увеличении объема/количества
        assert float(r.json()["delivery_price"]) >= 0

    @allure.title("Негативный тест: пустой список товаров")
    def test_empty_products_list(self, api):
        payload = {
            "delivery_method": 1,
            "receiver_city": 3,
            "order_products": []
        }
        r = api.calculate_delivery_price(**payload)
        # Ожидаем либо 0, либо 400 (Bad Request), так как нельзя рассчитать доставку пустого заказа
        assert r.status_code in [200, 400]