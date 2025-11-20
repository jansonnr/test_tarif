# tests/conftest.py
import pytest
from app_driver.wr_http_client import wrHttpClient


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        choices=["dev", "prod"],
        help="Environment: dev, prod"
    )


@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def base_url(env):
    from config import config
    return config.get_base_url(env)


@pytest.fixture(scope="session")
def http_client(base_url):
    """Используем готовый HttpClient из app_driver"""
    return wrHttpClient(base_url)


@pytest.fixture(scope="session")
def tariffs_data(http_client):
    """Основные данные из API"""
    response = http_client.tariff()
    response.raise_for_status()
    return response.json()