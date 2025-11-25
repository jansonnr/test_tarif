# tests/conftest.py
import pytest
from app_driver.wr_http_client import wrHttpClient
from test_logic.tariff_json import find_section_by_name

def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="dev",
        choices=["dev", "prod"]
    )

@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")

@pytest.fixture(scope="session")
def config():
    """Единая точка импорта конфигурации"""
    from config import config
    return config

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


@pytest.fixture(scope="session")
def snapshots_dir(env):
    from pathlib import Path
    snapshots_dir = Path("test_data") / "snapshots" / env
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    return snapshots_dir


@pytest.fixture(scope="session")
def section(tariffs_data, request):
    """Универсальная параметризованная фикстура для любой секции"""
    from test_logic.tariff_json import find_section_by_name

    section_name = request.param
    found_section = find_section_by_name(tariffs_data, section_name)

    if not found_section:
        pytest.skip(f"Секция '{section_name}' не найдена в API")

    return found_section


# ФИКСТУРЫ СЕКЦИЙ
SECTION_NAMES = [
    "Базис для ФЛ",
    "Базис для сотрудников",
    "Универсальный",
    "Госзаказ",
    "Платная лицензия (НЭП)",
    "Бизнес",
    "КЭП УЦ ФНС",
    "Перевыпуск АЦ",
    "Перевыпуск АЦ (Универсальный)",
    "ФТС",
    "ЕГАИС",
    "Рособрнадзор",
    "Росреестр"
]