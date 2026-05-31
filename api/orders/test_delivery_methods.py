import pytest
import allure
from core.orders import OrdersAPI


@allure.epic("Orders")
@allure.feature("Delivery Methods")
class TestDeliveryMethods:
    """Тесты для GET /web/v2/orders/delivery_methods/"""

    @pytest.fixture(scope="class")
    def api(self, auth_client):
        return OrdersAPI(auth_client)

    @allure.title("Успешное получение списка при валидном payment_method")
    def test_status_200(self, api):
        r = api.get_delivery_methods(payment_method_id=1)
        assert r.status_code == 200

    @allure.title("Проверка структуры списков enabled и disabled")
    def test_structure(self, api):
        data = api.get_delivery_methods(payment_method_id=1).json()
        assert "enabled" in data
        assert "disabled" in data
        assert isinstance(data["enabled"], list)
        assert isinstance(data["disabled"], list)

    @allure.title("Проверка полей каждого метода доставки")
    def test_method_fields(self, api):
        data = api.get_delivery_methods(payment_method_id=1).json()
        required = ["id", "name", "is_home_delivery", "is_active", "title", "order"]

        for method in data["enabled"]:
            for field in required:
                assert field in method, f"Поле {field} отсутствует в методе {method.get('name')}"
            assert isinstance(method["is_home_delivery"], bool)

    @allure.title("Локализация названий (title_*)")
    def test_localization(self, api):
        data = api.get_delivery_methods(payment_method_id=1).json()
        for method in data["enabled"]:
            assert method["title_uz"], f"Нет title_uz для {method['name']}"
            assert method["title_ru"], f"Нет title_ru для {method['name']}"
            assert method["title_en"], f"Нет title_en для {method['name']}"

    @allure.title("Проверка зависимости от payment_method (параметризованный тест)")
    @pytest.mark.parametrize("payment_id", [1])  # Можно добавить другие ID, если они есть
    def test_param_influence(self, api, payment_id):
        r = api.get_delivery_methods(payment_method_id=payment_id)
        assert r.status_code == 200
        # Если API поддерживает динамический список, здесь можно проверить
        # изменение состава методов при смене payment_method

    def test_empty_payment_method_param(self, api):
        # API должно либо вернуть 400, либо дефолтный список, но не 500
        r = api.client.get("/web/v2/orders/delivery_methods/?payment_method=")
        assert r.status_code != 500

    def test_home_delivery_flag(self, api):
        data = api.get_delivery_methods(payment_method_id=1).json()
        for method in data["enabled"]:
            if "door_to_door" in method["name"]:
                assert method[
                           "is_home_delivery"] is True, f"{method['name']} должен быть с флагом is_home_delivery=true"