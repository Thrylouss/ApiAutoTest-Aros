# api/product/test_variant_list.py
import pytest
from core.product import ProductAPI


class TestProductVariantList:
    """Тесты для GET /v1/product/product_variant_list/"""

    # --- Базовые smoke-проверки ---

    def test_status_200(self, guest_client):
        api = ProductAPI(guest_client)
        r = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz")
        assert r.status_code == 200

    def test_response_is_json(self, guest_client):
        api = ProductAPI(guest_client)
        r = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz")
        assert "application/json" in r.headers.get("content-type", "")

    # --- Структура пагинации ---

    def test_pagination_keys_present(self, guest_client):
        api = ProductAPI(guest_client)
        data = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz").json()
        for key in ("count", "next", "previous", "results"):
            assert key in data, f"Отсутствует ключ {key}"

    def test_count_is_positive_int(self, guest_client):
        api = ProductAPI(guest_client)
        data = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz").json()
        assert isinstance(data["count"], int)
        assert data["count"] > 0

    def test_first_page_previous_is_null(self, guest_client):
        api = ProductAPI(guest_client)
        data = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz").json()
        assert data["previous"] is None

    def test_first_page_next_is_url(self, guest_client):
        api = ProductAPI(guest_client)
        data = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz").json()
        # Если count > page_size, next должен быть ссылкой
        if data["count"] > 12:
            assert isinstance(data["next"], str)
            assert "page=2" in data["next"]

    # --- page_size ---

    @pytest.mark.parametrize("size", [1, 5, 12, 20])
    def test_page_size_respected(self, guest_client, size):
        api = ProductAPI(guest_client)
        data = api.get_variant_list(is_popular="true", page_size=size, page=1, lang="uz").json()
        assert len(data["results"]) <= size
        # На первой странице обычно ровно size, если count > size
        if data["count"] >= size:
            assert len(data["results"]) == size

    # --- page ---

    def test_pages_return_different_items(self, guest_client):
        api = ProductAPI(guest_client)
        page1 = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz").json()
        page2 = api.get_variant_list(is_popular="true", page_size=12, page=2, lang="uz").json()
        ids_1 = {item["id"] for item in page1["results"]}
        ids_2 = {item["id"] for item in page2["results"]}
        assert ids_1.isdisjoint(ids_2), "Страницы 1 и 2 содержат одинаковые id"

    def test_page_out_of_range_returns_404(self, guest_client):
        api = ProductAPI(guest_client)
        r = api.get_variant_list(is_popular="true", page_size=12, page=999999, lang="uz")
        assert r.status_code == 404

    # --- Структура результата ---

    REQUIRED_FIELDS = [
        "id", "category", "price", "quantity", "is_available",
        "attribute_values", "variation_quantity", "name", "images",
        "popularity_score", "product",
    ]

    def test_result_item_has_required_fields(self, guest_client):
        api = ProductAPI(guest_client)
        data = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz").json()
        assert len(data["results"]) > 0
        for item in data["results"]:
            for field in self.REQUIRED_FIELDS:
                assert field in item, f"В варианте id={item.get('id')} нет поля {field}"

    def test_id_is_unique_within_page(self, guest_client):
        api = ProductAPI(guest_client)
        data = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz").json()
        ids = [item["id"] for item in data["results"]]
        assert len(ids) == len(set(ids)), "В выдаче есть дубликаты id"

    def test_price_is_positive_number(self, guest_client):
        api = ProductAPI(guest_client)
        data = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz").json()
        for item in data["results"]:
            assert isinstance(item["price"], (int, float))
            assert item["price"] > 0, f"price <= 0 у варианта id={item['id']}"

    def test_quantity_is_non_negative(self, guest_client):
        api = ProductAPI(guest_client)
        data = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz").json()
        for item in data["results"]:
            assert item["quantity"] >= 0

    def test_is_available_matches_quantity(self, guest_client):
        """is_available=true ⇒ quantity > 0"""
        api = ProductAPI(guest_client)
        data = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz").json()
        for item in data["results"]:
            if item["is_available"]:
                assert item["quantity"] > 0, (
                    f"Вариант id={item['id']} помечен available, но quantity=0"
                )

    # --- Фильтр is_popular ---

    def test_is_popular_filter_returns_popular_items(self, guest_client):
        """При is_popular=true все варианты должны иметь популярность > 0"""
        api = ProductAPI(guest_client)
        data = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz").json()
        for item in data["results"]:
            assert item["popularity_score"] > 0, (
                f"Вариант id={item['id']} в is_popular, но popularity_score=0"
            )

    def test_is_popular_sorted_desc(self, guest_client):
        """Популярные обычно отсортированы по убыванию popularity_score"""
        api = ProductAPI(guest_client)
        data = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz").json()
        scores = [item["popularity_score"] for item in data["results"]]
        assert scores == sorted(scores, reverse=True), (
            f"Сортировка по popularity_score нарушена: {scores}"
        )

    # --- Локализация ---

    @pytest.mark.parametrize("lang", ["uz", "ru", "en"])
    def test_lang_param_accepted(self, guest_client, lang):
        api = ProductAPI(guest_client)
        r = api.get_variant_list(is_popular="true", page_size=12, page=1, lang=lang)
        assert r.status_code == 200

    def test_category_localized_name_present(self, guest_client):
        api = ProductAPI(guest_client)
        data = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz").json()
        for item in data["results"]:
            cat = item["category"]
            assert cat["name_uz"] and cat["name_ru"] and cat["name_en"]

    # --- Изображения ---

    def test_images_have_valid_urls(self, guest_client):
        api = ProductAPI(guest_client)
        data = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz").json()
        for item in data["results"]:
            for img in item["images"]:
                assert img["file"].startswith("http"), (
                    f"Невалидный URL картинки у варианта id={item['id']}"
                )

    # --- Скидка ---

    def test_discount_price_less_than_price(self, guest_client):
        """Цена скидки должна быть меньше базовой"""
        api = ProductAPI(guest_client)
        data = api.get_variant_list(is_popular="true", page_size=12, page=1, lang="uz").json()
        for item in data["results"]:
            if item.get("discount"):
                assert item["discount"]["price"] < item["price"], (
                    f"discount.price >= price у варианта id={item['id']}"
                )