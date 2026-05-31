class OrdersAPI:
    def __init__(self, client):
        self.client = client

    def get_payment_methods(self, **params):
        """
        GET /web/v2/orders/payment_methods/
        Возвращает список доступных методов оплаты
        """
        return self.client.get("/web/v2/orders/payment_methods/", params=params)

    def get_latest_order(self):
        """GET /web/v2/orders/latest-order/"""
        return self.client.get("/web/v2/orders/latest-order/")

    def get_delivery_methods(self, payment_method_id: int):
        """GET /web/v2/orders/delivery_methods/?payment_method={id}"""
        params = {"payment_method": payment_method_id}
        return self.client.get("/web/v2/orders/delivery_methods/", params=params)

    def get_order_page_addresses(self, region_id: int, delivery_method_id: int):
        """GET /web/v2/orders/order_page_addresses/"""
        params = {
            "region": region_id,
            "delivery_method": delivery_method_id
        }
        return self.client.get("/web/v2/orders/order_page_addresses/", params=params)

    def calculate_delivery_price(self, delivery_method: int, receiver_city: int, order_products: list):
        """
        POST /web/v2/orders/calculate_delivery_price/
        """
        payload = {
            "delivery_method": delivery_method,
            "receiver_city": receiver_city,
            "order_products": order_products
        }
        return self.client.post("/web/v2/orders/calculate_delivery_price/", json=payload)