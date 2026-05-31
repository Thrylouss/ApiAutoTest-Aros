import pytest
import allure
from core.orders import OrdersAPI


@allure.epic("Orders")
@allure.feature("Latest Order")
class TestLatestOrder:
    """Тесты для GET /web/v2/orders/latest-order/"""

    @pytest.fixture(scope="class")
    def api(self, auth_client):
        return OrdersAPI(auth_client)

    @allure.title("Успешное получение последнего заказа")
    def test_status_200(self, api):
        r = api.get_latest_order()
        assert r.status_code == 200

    @allure.title("Проверка структуры основных блоков заказа")
    def test_order_structure(self, api):
        data = api.get_latest_order().json()

        # Проверяем наличие ключевых вложенных объектов
        required_keys = ["id", "address", "region", "payment", "delivery", "warehouse", "created_datetime"]
        for key in required_keys:
            assert key in data, f"Ключ '{key}' отсутствует в ответе заказа"

    @allure.title("Проверка консистентности ID (адрес vs склад)")
    def test_ids_consistency(self, api):
        data = api.get_latest_order().json()
        # Проверяем, что ID адреса совпадает с ID склада (если бизнес-логика подразумевает это)
        assert data["address"]["id"] == data["warehouse"]["id"], "ID адреса и склада должны совпадать"

    @allure.title("Проверка типов цен (строки с десятичными числами)")
    def test_price_formats(self, api):
        data = api.get_latest_order().json()
        # В ответе цена приходит как строка "89000.00"
        assert isinstance(data["payment"]["total_amount"], str)
        assert float(data["payment"]["total_amount"]) > 0

    @allure.title("Проверка локализации вложенных объектов (регион)")
    def test_region_localization(self, api):
        data = api.get_latest_order().json()
        region_name = data["region"]["name"]
        for lang in ["en", "ru", "uz"]:
            assert lang in region_name, f"Локализация '{lang}' отсутствует в регионе"

    @allure.title("Проверка статусов заказа")
    def test_status_validity(self, api):
        data = api.get_latest_order().json()
        # Проверка, что статусы — это ожидаемые строки
        assert data["payment"]["status"] in ["pending", "paid", "canceled", "delivered"]
        assert data["delivery"]["status"] in ["pending", "courier_assigned", "delivered", "canceled"]