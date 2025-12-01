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
def tariffs_http_client(env):
    """Основные данные из API"""
    base_url = config.get_base_url(env)
    wr_http_client = wrHttpClient(base_url)
    tariffs_http_client = wr_http_client.tariff()
    return tariffs_http_client


@pytest.fixture(scope="session")
def snapshots_dir(env):
    """Директория со снепшотами для указанного окружения"""
    project_root = Path(__file__).parent
    snapshots_dir = project_root / "test_data" / "snapshots" / env
    return snapshots_dir


