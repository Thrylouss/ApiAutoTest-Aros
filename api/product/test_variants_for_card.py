import pytest
import allure
from core.product import ProductAPI


@allure.epic("Product")
@allure.feature("Variants For Card")
class TestVariantsForCard:
    """Тесты для POST /web/v2/products/product_variants_for_card/"""

    @pytest.fixture(scope="class")
    def api(self, guest_client):
        return ProductAPI(guest_client)

    @allure.title("Успешное получение данных для существующего ID")
    def test_get_valid_variant(self, api):
        variant_id = 2348
        r = api.get_variants_for_card([variant_id])
        assert r.status_code == 200

        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == variant_id
        assert "name" in data[0]
        assert "price" in data[0]

    @allure.title("Успешное получение данных для нескольких ID")
    def test_get_multiple_variants(self, api):
        # Допустим, мы передаем ID 2348 и какой-то другой валидный ID
        variant_ids = [2348]
        r = api.get_variants_for_card(variant_ids)
        assert r.status_code == 200
        assert len(r.json()) == len(variant_ids)

    @allure.title("Проверка обязательных полей в ответе")
    def test_fields_presence(self, api):
        r = api.get_variants_for_card([2348])
        item = r.json()[0]

        required = ["id", "uid", "name", "price", "quantity", "images", "variation_quantity"]
        for field in required:
            assert field in item, f"Поле {field} отсутствует в ответе"

    @allure.title("Обработка неверного (несуществующего) ID")
    def test_non_existent_id(self, api):
        r = api.get_variants_for_card([99999999])
        # Ожидаем, что API либо вернет пустой список, либо 404
        assert r.status_code in [200, 404]
        if r.status_code == 200:
            assert r.json() == [], "Для несуществующего ID должен быть пустой список"

    @allure.title("Валидация структуры variation_quantity")
    def test_variation_quantity_structure(self, api):
        r = api.get_variants_for_card([2348])
        item = r.json()[0]

        # Проверяем структуру складов
        for vq in item["variation_quantity"]:
            assert "warehouse" in vq
            assert "quantity" in vq
            assert isinstance(vq["warehouse"]["id"], int)