import pytest
from core.cart import CartAPI
from core.product import ProductAPI


class TestCartAddItems:
    """Тесты для POST /web/v2/cart/items/add/"""

    @pytest.fixture(scope="class")
    def valid_variant(self, auth_client):
        """
        Фикстура динамически находит 1 доступный товар (is_available=True, quantity>0)
        через ProductAPI, чтобы тесты корзины всегда имели актуальный ID.
        """
        product_api = ProductAPI(auth_client)
        r = product_api.get_variant_list(is_popular="true", page_size=20, page=1, lang="ru")
        assert r.status_code == 200, "Не удалось получить список товаров"

        for item in r.json().get("results", []):
            if item.get("is_available") and item.get("quantity", 0) > 0:
                return {
                    "id": item["id"],
                    "stock": item["quantity"]
                }
        pytest.skip("На первой странице нет доступных товаров для теста корзины")

    # --- Базовые smoke-проверки ---

    def test_status_201_created(self, auth_client, valid_variant):
        api = CartAPI(auth_client)
        payload = [{"product_variant": valid_variant["id"], "quantity": 1}]
        r = api.add_item(payload=payload)
        assert r.status_code == 201

    def test_response_is_json(self, auth_client, valid_variant):
        api = CartAPI(auth_client)
        payload = [{"product_variant": valid_variant["id"], "quantity": 1}]
        r = api.add_item(payload=payload)
        assert "application/json" in r.headers.get("content-type", "")

    # --- Структура результата ---

    def test_response_is_list(self, auth_client, valid_variant):
        api = CartAPI(auth_client)
        payload = [{"product_variant": valid_variant["id"], "quantity": 1}]
        data = api.add_item(payload=payload).json()
        assert isinstance(data, list), "Ответ должен быть массивом (list)"

    def test_response_contains_required_keys(self, auth_client, valid_variant):
        api = CartAPI(auth_client)
        payload = [{"product_variant": valid_variant["id"], "quantity": 1}]
        data = api.add_item(payload=payload).json()

        assert len(data) == 1
        item = data[0]
        assert "product_variant" in item, "Отсутствует ключ product_variant"
        assert "quantity" in item, "Отсутствует ключ quantity"

    def test_response_values_match_request(self, auth_client, valid_variant):
        api = CartAPI(auth_client)
        payload = [{"product_variant": valid_variant["id"], "quantity": 2}]
        data = api.add_item(payload=payload).json()

        item = data[0]
        assert item["product_variant"] == valid_variant["id"], "Вернулся неверный ID товара"
        assert item["quantity"] == 2, "Вернулось неверное количество"

    # --- Бизнес-логика параметра quantity ---

    def test_add_max_available_quantity(self, auth_client, valid_variant):
        api = CartAPI(auth_client)
        # Пробуем добавить весь доступный остаток на складе
        max_qty = valid_variant["stock"]
        payload = [{"product_variant": valid_variant["id"], "quantity": max_qty}]
        r = api.add_item(payload=payload)
        assert r.status_code == 201

    def test_add_zero_quantity_returns_error(self, auth_client, valid_variant):
        api = CartAPI(auth_client)
        payload = [{"product_variant": valid_variant["id"], "quantity": 0}]
        r = api.add_item(payload=payload)
        # Ожидаем ошибку валидации (Bad Request / Unprocessable Entity)
        assert r.status_code in [400, 422], "Добавление 0 товаров должно вызывать ошибку"

    def test_add_negative_quantity_returns_error(self, auth_client, valid_variant):
        api = CartAPI(auth_client)
        payload = [{"product_variant": valid_variant["id"], "quantity": -5}]
        r = api.add_item(payload=payload)
        assert r.status_code in [400, 422], "Отрицательное количество не должно приниматься"

    def test_add_quantity_exceeding_stock(self, auth_client, valid_variant):
        api = CartAPI(auth_client)
        # Пытаемся добавить больше, чем есть на складе
        huge_qty = valid_variant["stock"] + 99999
        payload = [{"product_variant": valid_variant["id"], "quantity": huge_qty}]
        r = api.add_item(payload=payload)
        # В зависимости от бизнес-логики: либо 400, либо сервер сохранит только доступный максимум
        assert r.status_code in [400, 409, 422], "Превышение остатка должно обрабатываться с ошибкой"

    # --- Валидация параметра product_variant ---

    def test_add_non_existent_product(self, auth_client):
        api = CartAPI(auth_client)
        payload = [{"product_variant": 999999999, "quantity": 1}]
        r = api.add_item(payload=payload)
        # Товар не найден (404) или ошибка валидации ключа (400)
        assert r.status_code in [400, 404]

    def test_add_missing_product_variant(self, auth_client):
        api = CartAPI(auth_client)
        payload = [{"quantity": 1}]  # Убрали product_variant
        r = api.add_item(payload=payload)
        assert r.status_code in [400, 422]

    # --- Структура Payload (Массив) ---

    def test_add_multiple_items_at_once(self, auth_client, valid_variant):
        """Проверка мульти-добавления, если в массиве передать несколько товаров"""
        api = CartAPI(auth_client)
        payload = [
            {"product_variant": valid_variant["id"], "quantity": 1},
            {"product_variant": valid_variant["id"], "quantity": 2}
        ]
        r = api.add_item(payload=payload)
        # Проверяем, что API может обрабатывать списки с >1 элементами
        assert r.status_code == 201
        data = r.json()
        assert len(data) == 2, "Ожидалось, что в ответе вернутся оба объекта"

    def test_empty_list_payload(self, auth_client):
        api = CartAPI(auth_client)
        payload = []
        r = api.add_item(payload=payload)
        # Пустой массив не должен приводить к 500 ошибке сервера
        assert r.status_code in [400, 422], "Пустой массив должен вызывать ошибку валидации"