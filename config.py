from environs import Env
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

env = Env()
env.read_env()

class Config:

    def __init__(self):
        self.ENV = env.str("ENV", "dev")

        self.API_URLS = {
        "dev": env.str("DEV_API_URL", "http://reg-api-test.keydisk.ru/"),
        "prod": env.str("PROD_API_URL", "https://reg-api.keydisk.ru/"),
        }

        self.snapshots_dir_et = BASE_DIR / 'test_data' / 'snapshots' / self.ENV
        self.snapshots_dir_1c = BASE_DIR / 'test_data' / 'snapshots_1c' / self.ENV

    def get_base_url(self, env_name):
        env_name = env_name or self.ENV
        return self.API_URLS.get(env_name, self.API_URLS['dev'])

config = Config()