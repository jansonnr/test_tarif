# config.py
from environs import Env
from typing import Dict

env = Env()
env.read_env()


class Config:
    """Конфигурация приложения"""

    # Окружение по умолчанию
    ENV = env.str("ENV", "dev")

    # URL API для разных окружений
    API_URLS = {
        "dev": env.str("DEV_API_URL", "http://reg-api-test.keydisk.ru/"),
        "prod": env.str("PROD_API_URL", "https://reg-api.keydisk.ru/"),
    }

    @classmethod
    def get_base_url(cls, env_name: str = None) -> str:
        """Получает базовый URL для указанного окружения"""
        env_name = env_name or cls.ENV
        # Используем 'dev' как fallback, а не 'dev-1'
        return cls.API_URLS.get(env_name, cls.API_URLS["dev"])

    @classmethod
    def is_dev(cls) -> bool:
        """Проверяет что текущее окружение - разработка"""
        return cls.ENV == "dev"

    @classmethod
    def is_prod(cls) -> bool:
        """Проверяет что текущее окружение - продакшен"""
        return cls.ENV == "prod"


# Создаем глобальный экземпляр конфигурации
config = Config()