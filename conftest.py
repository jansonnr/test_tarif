import pytest

def pytest_addoption(parser):
    parser.addoption("--env", action="store", default="staging",
                    help="Environment: staging, prod")
    parser.addoption("--update-snapshots", action="store_true",
                    help="Update snapshots for current environment")

@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def base_url(env):
    urls = {
        "staging": "http://reg-api-test.keydisk.ru/",
        "prod": "https://reg-api.keydisk.ru/"
    }
    return urls.get(env, urls["staging"])

@pytest.fixture(scope="session")
def snapshots_dir(env):
    return f"test_data/fixtures/snapshots/{env}"

@pytest.fixture(scope="session")
def expected_data_dir(env):
    return f"tests/fixtures/expected_data/{env}"