import pytest
import json
from pathlib import Path
from test_logic.tariff_json import get_all_sections
from config import config
from app_driver.wr_http_client import wrHttpClient


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
def base_url(env):
    """Базовый URL для API"""
    url = config.get_base_url(env)
    return url


@pytest.fixture(scope="session")
def http_client(base_url):
    """Используем готовый HttpClient из app_driver"""
    return wrHttpClient(base_url)


@pytest.fixture(scope="session")
def tariffs_data(http_client):
    """Основные данные из API"""
    response = http_client.tariff()
    response.raise_for_status()
    data = response.json()
    return data


@pytest.fixture(scope="session")
def snapshots_dir(env):
    """Директория со снепшотами для указанного окружения"""
    project_root = Path(__file__).parent
    snapshots_dir = project_root / "test_data" / "snapshots" / env
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    return snapshots_dir


@pytest.fixture(scope="session")
def snapshot_tariffs_data(snapshots_dir):
    """Загружает данные из сохраненного снепшота (JSON файла)"""
    snapshot_path = snapshots_dir / "tariffs_response.json"
    with open(snapshot_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data


@pytest.fixture(scope="session")
def common_sections(tariffs_data, snapshot_tariffs_data):
    """Находит секции которые есть и в API и в снепшоте"""
    # Получаем все секции из API
    api_sections = get_all_sections(tariffs_data)
    # Получаем все секции из снепшота
    snapshot_sections = get_all_sections(snapshot_tariffs_data)
    # Собираем множества имен секций
    api_names = {s["sectionName"] for s in api_sections}
    snapshot_names = {s["sectionName"] for s in snapshot_sections}
    # Находим пересечение - секции которые есть в обоих источниках
    common = api_names & snapshot_names

    # Возвращаем отсортированный список общих секций
    return sorted(common)

@pytest.fixture(scope="session")
def snapshot_files(snapshots_dir):
    """Возвращает все файлы снепшотов секций"""
    section_files = list(snapshots_dir.glob("section_*.json"))
    return section_files