import pytest
import allure
from core.orders import OrdersAPI


@allure.epic("Orders")
@allure.feature("Payment Methods")
class TestPaymentMethods:
    """Тесты для GET /web/v2/orders/payment_methods/"""

    @pytest.fixture(scope="class")
    def api(self, auth_client):
        # Если методы оплаты доступны без авторизации,
        # можно заменить auth_client на guest_client
        return OrdersAPI(auth_client)

    # --- Базовые smoke-проверки ---

    @allure.title("Успешный статус ответа 200")
    def test_status_200(self, api):
        r = api.get_payment_methods()
        assert r.status_code == 200

    @allure.title("Формат ответа - JSON")
    def test_response_is_json(self, api):
        r = api.get_payment_methods()
        assert "application/json" in r.headers.get("content-type", "")

    # --- Структура результата ---

    @allure.title("Ответ является списком (массивом)")
    def test_response_is_list(self, api):
        data = api.get_payment_methods().json()
        assert isinstance(data, list), "Ожидался ответ в виде списка (массива)"
        assert len(data) > 0, "Список методов оплаты пуст"

    REQUIRED_FIELDS = [
        "id", "name", "is_active", "title",
        "title_uz", "title_en", "title_ru",
        "description", "description_uz", "description_en", "description_ru",
        "icon"
    ]

    @allure.title("Каждый метод оплаты содержит все обязательные поля")
    def test_payment_method_has_required_fields(self, api):
        data = api.get_payment_methods().json()
        for method in data:
            for field in self.REQUIRED_FIELDS:
                assert field in method, f"В методе оплаты id={method.get('id')} отсутствует поле '{field}'"

    # --- Проверка типов данных и значений ---

    @allure.title("Проверка типов данных (id, name, is_active)")
    def test_data_types(self, api):
        data = api.get_payment_methods().json()
        for method in data:
            assert isinstance(method["id"], int), "ID должен быть числом"
            assert isinstance(method["name"], str), "Name должен быть строкой"
            assert isinstance(method["is_active"], bool), "is_active должен быть булевым значением"

    @allure.title("ID методов оплаты уникальны")
    def test_ids_are_unique(self, api):
        data = api.get_payment_methods().json()
        ids = [method["id"] for method in data]
        assert len(ids) == len(set(ids)), "В списке есть дублирующиеся ID методов оплаты"

    @allure.title("Внутренние имена (name) уникальны и не пусты")
    def test_names_are_unique_and_valid(self, api):
        data = api.get_payment_methods().json()
        names = [method["name"] for method in data]

        assert len(names) == len(set(names)), "В списке есть дублирующиеся значения name"
        for name in names:
            assert len(name.strip()) > 0, "Поле name не должно быть пустым"

    # --- Локализация ---

    @allure.title("Проверка наличия локализованных названий (title_*)")
    def test_localization_titles_present(self, api):
        data = api.get_payment_methods().json()
        for method in data:
            assert method["title_uz"], f"Отсутствует title_uz у метода {method['name']}"
            assert method["title_ru"], f"Отсутствует title_ru у метода {method['name']}"
            assert method["title_en"], f"Отсутствует title_en у метода {method['name']}"

    # --- Вложенные объекты (Иконки) ---

    @allure.title("Проверка структуры и ссылок внутри объекта icon")
    def test_icon_structure_and_urls(self, api):
        data = api.get_payment_methods().json()
        for method in data:
            icon = method.get("icon")
            if icon is not None:
                assert "id" in icon
                assert "file" in icon

                file_url = icon.get("file")
                # Проверяем, что ссылка либо абсолютная (http), либо относительная медиа-ссылка (/media/)
                assert file_url.startswith("http") or file_url.startswith("/media/"), (
                    f"Невалидный URL иконки: {file_url}"
                )