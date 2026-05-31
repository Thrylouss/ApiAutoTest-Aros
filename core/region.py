class RegionAPI:
    def __init__(self, client):
        self.client = client

    def get_regions(self, page=1, page_size=15):
        """GET /v1/region/regions/"""
        params = {"page": page, "page_size": page_size}
        return self.client.get("/v1/region/regions/", params=params)