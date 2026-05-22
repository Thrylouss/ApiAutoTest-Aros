# core/product.py

class ProductAPI:
    def __init__(self, client):
        self.client = client

    def get_product(self, endpoint):
        """Универсальный GET по /v1/product{endpoint}"""
        return self.client.get(f"/v1/product{endpoint}")

    def get_variant_list(self, **params):
        """
        GET /v1/product/product_variant_list/
        Пример: get_variant_list(is_popular="true", page_size=12, page=1, lang="uz")
        """
        return self.client.get("/v1/product/product_variant_list/", params=params)

    def get_variant_siblings(self, variant_id: int, **params):
        """
        GET /web/v2/products/product_variant/siblings/{variant_id}/
        Лежит на другом префиксе (/web/v2/), поэтому отдельный метод.
        """
        return self.client.get(
            f"/web/v2/products/product_variant/siblings/{variant_id}/",
            params=params,
        )