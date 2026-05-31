import pytest
import allure
from core.orders import OrdersAPI


@allure.epic("Orders")
@allure.feature("Order Addresses")
class TestOrderPageAddresses:
    """Тесты для GET /web/v2/orders/order_page_addresses/"""

    @pytest.fixture(scope="class")
    def api(self, auth_client):
        return OrdersAPI(auth_client)

    @allure.title("Успешный статус ответа 200")
    def test_status_200(self, api):
        r = api.get_order_page_addresses(region_id=1, delivery_method_id=2)
        assert r.status_code == 200

    @allure.title("Проверка обязательных полей адреса")
    def test_address_fields(self, api):
        data = api.get_order_page_addresses(region_id=1, delivery_method_id=2).json()
        assert len(data) > 0, "Список адресов пуст для валидных параметров"

        required = ["id", "name", "street", "latitude", "longitude", "phone_number", "region"]
        for addr in data:
            for field in required:
                assert field in addr, f"Поле {field} отсутствует в адресе id={addr['id']}"

    @allure.title("Валидация координат (latitude/longitude)")
    def test_coordinates_validity(self, api):
        data = api.get_order_page_addresses(region_id=1, delivery_method_id=2).json()
        for addr in data:
            # Координаты приходят как строки, проверяем, что их можно превратить в float
            assert float(addr["latitude"]) != 0
            assert float(addr["longitude"]) != 0

    @allure.title("Фильтрация: регион адреса соответствует запрошенному")
    def test_region_filtering(self, api):
        region_id = 3  # Например, Чиланзар
        data = api.get_order_page_addresses(region_id=region_id, delivery_method_id=2).json()

        for addr in data:
            assert addr["region"]["id"] == region_id, (
                f"Адрес {addr['name']} (id={addr['id']}) не относится к региону {region_id}"
            )

    @allure.title("Негативный тест: пустой список при несуществующем регионе")
    def test_invalid_region(self, api):
        r = api.get_order_page_addresses(region_id=9999, delivery_method_id=2)
        assert r.status_code == 200
        assert r.json() == [], "Для несуществующего региона список должен быть пустым"