import pytest
from core.cart import CartAPI
from core.product import ProductAPI


class TestCartDelete:
    """Тесты для удаления товаров и очистки корзины (DELETE)"""

    @pytest.fixture(scope="function")
    def valid_variant(self, auth_client):
        """Находит 1 доступный товар и возвращает его ID"""
        product_api = ProductAPI(auth_client)
        r = product_api.get_variant_list(is_popular="true", page_size=20, page=1, lang="ru")
        assert r.status_code == 200

        for item in r.json().get("results", []):
            if item.get("is_available") and item.get("quantity", 0) > 0:
                return item["id"]
        pytest.skip("Нет доступных товаров для теста")

    @pytest.fixture(scope="function")
    def cart_with_item(self, auth_client, valid_variant):
        """
        Фикстура:
        1. Добавляет товар в корзину (Setup)
        2. Передает variant_id в тест
        3. Очищает корзину после теста (Teardown), чтобы сохранить чистоту базы
        """
        api = CartAPI(auth_client)
        # Setup: добавляем товар
        api.add_item([{"product_variant": valid_variant, "quantity": 1}])

        yield valid_variant  # Передаем ID в тест

        # Teardown: очищаем корзину (даже если тест упал)
        api.clear_cart()

    # --- Тесты для DELETE /web/v2/cart/items/delete/{variant_id}/ ---

    def test_delete_existing_item(self, auth_client, cart_with_item):
        """Позитивный тест: удаление существующего товара из корзины"""
        api = CartAPI(auth_client)
        variant_id = cart_with_item

        r = api.delete_item(variant_id=variant_id)

        # Обычно DELETE возвращает 204 No Content или 200 OK
        assert r.status_code in [200, 204], f"Ошибка при удалении: {r.text}"

    def test_delete_item_twice_returns_error(self, auth_client, cart_with_item):
        """Негативный тест: повторное удаление того же товара"""
        api = CartAPI(auth_client)
        variant_id = cart_with_item

        # Удаляем первый раз (успешно)
        api.delete_item(variant_id=variant_id)

        # Пытаемся удалить повторно
        r_second = api.delete_item(variant_id=variant_id)

        # Товар уже удален, ожидаем 404 Not Found
        assert r_second.status_code == 404, "Повторное удаление должно возвращать 404"

    def test_delete_non_existent_item(self, auth_client):
        """Негативный тест: удаление товара, которого нет в корзине"""
        api = CartAPI(auth_client)
        fake_id = 999999999

        r = api.delete_item(variant_id=fake_id)
        assert r.status_code == 404

    def test_delete_invalid_id_type(self, auth_client):
        """Негативный тест: передача строки вместо ID"""
        api = CartAPI(auth_client)
        invalid_id = "abc"

        r = api.delete_item(variant_id=invalid_id)
        # Ожидаем ошибку валидации пути (404 или 400 в зависимости от роутера Django)
        assert r.status_code in [400, 404]

    # --- Тесты для DELETE /web/v2/cart/items/clear/ ---

    def test_clear_cart_with_items(self, auth_client, valid_variant):
        """Позитивный тест: полная очистка корзины, в которой есть товары"""
        api = CartAPI(auth_client)

        # Добавляем 2 единицы товара
        api.add_item([{"product_variant": valid_variant, "quantity": 2}])

        r = api.clear_cart()
        assert r.status_code in [200, 204], f"Очистка корзины завершилась с ошибкой: {r.text}"

    def test_clear_empty_cart(self, auth_client):
        """Пограничный случай: очистка уже пустой корзины"""
        api = CartAPI(auth_client)

        # Сначала гарантированно очищаем
        api.clear_cart()

        # Вызываем очистку повторно
        r = api.clear_cart()

        # Система не должна падать с 500 ошибкой. Должен быть успешный статус (200/204)
        # или информативный 400 (если логика запрещает очищать пустую). Чаще всего это 200/204.
        assert r.status_code in [200, 204, 400], "Очистка пустой корзины не должна ломать сервер"