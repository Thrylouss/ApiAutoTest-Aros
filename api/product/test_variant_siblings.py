# api/product/test_variant_siblings.py
import pytest
from core.product import ProductAPI


# Известный валидный variant_id из продакшна (Xiaomi Redmi 6/6A, product=1544)
VALID_VARIANT_ID = 2348
EXPECTED_PRODUCT_ID = 1544


class TestProductVariantSiblings:
    """Тесты для GET /web/v2/products/product_variant/siblings/{id}/"""

    # --- Базовые smoke ---

    def test_status_200_for_valid_id(self, guest_client):
        api = ProductAPI(guest_client)
        r = api.get_variant_siblings(VALID_VARIANT_ID)
        assert r.status_code == 200

    def test_response_is_list(self, guest_client):
        """Эндпоинт возвращает массив без пагинации"""
        api = ProductAPI(guest_client)
        data = api.get_variant_siblings(VALID_VARIANT_ID).json()
        assert isinstance(data, list)

    def test_response_not_empty(self, guest_client):
        """У существующего варианта должны быть siblings (как минимум сам он)"""
        api = ProductAPI(guest_client)
        data = api.get_variant_siblings(VALID_VARIANT_ID).json()
        assert len(data) > 0

    # --- Ключевая логика: все siblings того же продукта ---

    def test_all_siblings_share_same_product(self, guest_client):
        """Все варианты в выдаче должны принадлежать одному product"""
        api = ProductAPI(guest_client)
        data = api.get_variant_siblings(VALID_VARIANT_ID).json()
        product_ids = {item["product"] for item in data}
        assert len(product_ids) == 1, (
            f"siblings содержат варианты разных продуктов: {product_ids}"
        )
        assert product_ids.pop() == EXPECTED_PRODUCT_ID

    def test_requested_variant_in_siblings(self, guest_client):
        """Сам запрашиваемый вариант должен присутствовать в siblings"""
        api = ProductAPI(guest_client)
        data = api.get_variant_siblings(VALID_VARIANT_ID).json()
        ids = [item["id"] for item in data]
        assert VALID_VARIANT_ID in ids

    def test_siblings_share_same_category(self, guest_client):
        """Логично, что siblings одного продукта в одной категории"""
        api = ProductAPI(guest_client)
        data = api.get_variant_siblings(VALID_VARIANT_ID).json()
        category_ids = {item["category"]["id"] for item in data}
        assert len(category_ids) == 1

    def test_no_duplicate_ids(self, guest_client):
        api = ProductAPI(guest_client)
        data = api.get_variant_siblings(VALID_VARIANT_ID).json()
        ids = [item["id"] for item in data]
        assert len(ids) == len(set(ids)), "В siblings найдены дубликаты id"

    # --- Структура полей ---

    REQUIRED_FIELDS = [
        "id", "category", "price", "quantity", "is_available",
        "attribute_values", "name", "images", "product",
    ]

    def test_each_sibling_has_required_fields(self, guest_client):
        api = ProductAPI(guest_client)
        data = api.get_variant_siblings(VALID_VARIANT_ID).json()
        for item in data:
            for field in self.REQUIRED_FIELDS:
                assert field in item, f"В sibling id={item.get('id')} нет поля {field}"

    def test_siblings_differ_in_attributes(self, guest_client):
        """
        Siblings отличаются комбинацией атрибутов (цвет/качество/...).
        Если их больше одного, набор attribute_values должен различаться.
        """
        api = ProductAPI(guest_client)
        data = api.get_variant_siblings(VALID_VARIANT_ID).json()
        if len(data) < 2:
            pytest.skip("Для проверки нужно минимум 2 sibling")

        signatures = []
        for item in data:
            sig = tuple(sorted(av["id"] for av in item["attribute_values"]))
            signatures.append(sig)
        assert len(signatures) == len(set(signatures)), (
            "Найдены siblings с идентичным набором атрибутов"
        )

    # --- Доступность ---

    def test_is_available_consistent_with_quantity(self, guest_client):
        api = ProductAPI(guest_client)
        data = api.get_variant_siblings(VALID_VARIANT_ID).json()
        for item in data:
            if item["is_available"]:
                assert item["quantity"] > 0
            else:
                # Неактивный вариант — quantity может быть 0
                pass

    def test_price_positive(self, guest_client):
        api = ProductAPI(guest_client)
        data = api.get_variant_siblings(VALID_VARIANT_ID).json()
        for item in data:
            assert item["price"] > 0

    # --- Негативные сценарии ---

    def test_non_existing_id_returns_404_or_empty(self, guest_client):
        """
        Для несуществующего id ожидаем либо 404, либо пустой список —
        зависит от реализации, фиксируем оба валидных поведения.
        """
        api = ProductAPI(guest_client)
        r = api.get_variant_siblings(99999999)
        assert r.status_code in (200, 404)
        if r.status_code == 200:
            assert r.json() == []

    def test_string_id_returns_4xx(self, guest_client):
        api = ProductAPI(guest_client)
        r = api.get_variant_siblings("abc")
        assert 400 <= r.status_code < 500

    def test_negative_id_returns_4xx(self, guest_client):
        api = ProductAPI(guest_client)
        r = api.get_variant_siblings(-1)
        assert r.status_code in (400, 404)

    # --- Локализация ---

    @pytest.mark.parametrize("lang", ["uz", "ru", "en"])
    def test_lang_param_accepted(self, guest_client, lang):
        api = ProductAPI(guest_client)
        r = api.get_variant_siblings(VALID_VARIANT_ID, lang=lang)
        assert r.status_code == 200

    # --- Авторизованный клиент тоже должен работать ---

    def test_works_with_auth_client(self, auth_client):
        api = ProductAPI(auth_client)
        r = api.get_variant_siblings(VALID_VARIANT_ID)
        assert r.status_code == 200