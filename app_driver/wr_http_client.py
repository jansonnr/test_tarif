import requests
from config import config


class wrHttpClient:
    """Класс, инкапсулирующий Http запросы к тестируемуму приложению"""

    def __init__(self, env: str = None):

        self.env = env or config.ENV
        self.base_url = config.get_base_url(self.env)

    def tariff_et(self) -> requests.Response:
        return requests.get(self.base_url + '/api/v1/request/getpriceinfo?priceTypeId=32')

    def tariff_1c(self) -> requests.Response:
        return requests.get(self.base_url + '/api/v1/request/getpriceinfo?priceTypeId=33')