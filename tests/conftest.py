# tests/conftest.py
import pytest
import sys
import os
from pathlib import Path

# ДОБАВЛЯЕМ КОРЕНЬ ПРОЕКТА В PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Теперь можно импортировать модули
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
    """Базовый URL"""
    try:
        from config import config
        return config.get_base_url(env)
    except Exception as e:
        print(f"⚠️  Config error: {e}, using fallback URLs")
        urls = {
            "dev": "http://reg-api-test.keydisk.ru/",
            "prod": "https://reg-api.keydisk.ru/"
        }
        return urls.get(env, urls["dev"])


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
    """Директория со снепшотами"""
    snapshots_dir = project_root / "test_data" / "snapshots" / env
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    return snapshots_dir


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


@pytest.fixture(scope="session")
def section(tariffs_data, request):
    """Универсальная параметризованная фикстура для любой секции"""
    from test_logic.tariff_json import find_section_by_name

    section_name = request.param
    found_section = find_section_by_name(tariffs_data, section_name)

    if not found_section:
        pytest.skip(f"Секция '{section_name}' не найдена в API")

    return found_section


# ИНДИВИДУАЛЬНЫЕ ФИКСТУРЫ ДЛЯ ОСНОВНЫХ СЕКЦИЙ
@pytest.fixture(scope="session")
def basis_fl_section(tariffs_data):
    from test_logic.tariff_json import find_section_by_name
    section = find_section_by_name(tariffs_data, "Базис для ФЛ")
    assert section is not None
    return section


@pytest.fixture(scope="session")
def basis_employees_section(tariffs_data):
    from test_logic.tariff_json import find_section_by_name
    section = find_section_by_name(tariffs_data, "Базис для сотрудников")
    assert section is not None
    return section


@pytest.fixture(scope="session")
def universal_section(tariffs_data):
    from test_logic.tariff_json import find_section_by_name
    section = find_section_by_name(tariffs_data, "Универсальный")
    assert section is not None
    return section