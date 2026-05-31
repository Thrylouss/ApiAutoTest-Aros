class CartAPI:
    def __init__(self, client):
        self.client = client

    def add_item(self, payload: list):
        return self.client.post("/web/v2/cart/items/add/", json=payload)

    def delete_item(self, variant_id: int):
        """
        DELETE /web/v2/cart/items/delete/{variant_id}/
        Удаляет конкретный вариант продукта из корзины
        """
        return self.client.delete(f"/web/v2/cart/items/delete/{variant_id}/")

    def clear_cart(self):
        """
        DELETE /web/v2/cart/items/clear/
        Полностью очищает корзину
        """
        return self.client.delete("/web/v2/cart/items/clear/")