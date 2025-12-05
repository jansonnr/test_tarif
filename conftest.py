import pytest
from pathlib import Path
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
def tariffs_http_client_et(env):
    """Основные данные из API"""
    base_url = config.get_base_url(env)
    wr_http_client = wrHttpClient(base_url)
    tariffs_http_client_et = wr_http_client.tariff_et()
    return tariffs_http_client_et

@pytest.fixture(scope="session")
def tariffs_http_client_1c(env):
    """Основные данные из API"""
    base_url = config.get_base_url(env)
    wr_http_client = wrHttpClient(base_url)
    tariffs_http_client_1c = wr_http_client.tariff_1c()
    return tariffs_http_client_1c


@pytest.fixture(scope="session")
def snapshots_dir_et(env):
    """Директория со снепшотами для указанного окружения"""
    project_root = Path(__file__).parent
    snapshots_dir_et = project_root / "test_data" / "snapshots" / env
    return snapshots_dir_et

def snapshots_dir_1c(env):
    """Директория со снепшотами для указанного окружения"""
    project_root = Path(__file__).parent
    snapshots_dir_c = project_root / "test_data" / "snapshots_1c" / env
    return snapshots_dir_c