import pytest
import allure
from core.region import RegionAPI


@allure.epic("Core")
@allure.feature("Regions")
class TestRegions:
    """Тесты для GET /v1/region/regions/"""

    @pytest.fixture(scope="class")
    def api(self, guest_client):
        return RegionAPI(guest_client)

    @allure.title("Успешный статус ответа 200")
    def test_status_200(self, api):
        assert api.get_regions().status_code == 200

    @allure.title("Проверка обязательных полей в объекте региона")
    def test_region_structure(self, api):
        data = api.get_regions().json()
        results = data.get("results", [])

        required_fields = ["id", "warehouses_count", "name", "region_code", "has_shipping"]

        for region in results:
            for field in required_fields:
                assert field in region, f"Поле {field} отсутствует в регионе id={region.get('id')}"

            # Проверка структуры объекта name
            name_obj = region["name"]
            for lang in ["en", "ru", "uz"]:
                assert lang in name_obj, f"Локализация '{lang}' отсутствует в name для id={region['id']}"

    @allure.title("Проверка типов данных")
    def test_data_types(self, api):
        data = api.get_regions().json()
        for region in data["results"]:
            assert isinstance(region["id"], int)
            assert isinstance(region["warehouses_count"], int)
            assert isinstance(region["has_shipping"], bool)
            assert isinstance(region["region_code"], int)

    @allure.title("Уникальность ID регионов")
    def test_ids_are_unique(self, api):
        data = api.get_regions().json()
        ids = [r["id"] for r in data["results"]]
        assert len(ids) == len(set(ids)), "Найдены дубликаты ID регионов"

    @allure.title("Проверка region_code (логический тест)")
    def test_region_code_uniqueness(self, api):
        """
        Примечание: В данных есть регионы с одинаковым region_code=123.
        Этот тест поймает это и потребует уточнения бизнес-логики.
        """
        data = api.get_regions().json()
        codes = [r["region_code"] for r in data["results"]]

        # Если это баг данных, тест упадет. Если так и задумано, удали этот тест.
        unique_codes = set(codes)
        assert len(codes) == len(unique_codes), f"Дублирующиеся region_code найдены: {codes}"