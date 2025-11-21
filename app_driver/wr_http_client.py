import requests


class wrHttpClient:
    """Класс, инкапсулирующий Http запросы к тестируемуму приложению"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    def tariff(self) -> requests.Response:
        return requests.get(self.base_url + '/api/v1/request/getpriceinfo?priceTypeId=32')