import pytest
from test_logic.tariff_json import find_section_by_name

# СПИСОК ВСЕХ СЕКЦИЙ ДЛЯ ПАРАМЕТРИЗАЦИИ
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
    section_name = request.param
    found_section = find_section_by_name(tariffs_data, section_name)

    if not found_section:
        pytest.skip(f"Секция '{section_name}' не найдена в API")

    return found_section


# ИНДИВИДУАЛЬНЫЕ ФИКСТУРЫ ДЛЯ ОСНОВНЫХ СЕКЦИЙ
@pytest.fixture(scope="session")
def basis_fl_section(tariffs_data):
    section = find_section_by_name(tariffs_data, "Базис для ФЛ")
    assert section is not None
    return section


@pytest.fixture(scope="session")
def basis_employees_section(tariffs_data):
    section = find_section_by_name(tariffs_data, "Базис для сотрудников")
    assert section is not None
    return section


@pytest.fixture(scope="session")
def universal_section(tariffs_data):
    section = find_section_by_name(tariffs_data, "Универсальный")
    assert section is not None
    return section