# tests/test_api_vs_snapshots.py
import pytest
import json
from pathlib import Path
from test_logic.tariff_json import find_section_by_name, find_tariff_by_name, get_all_sections


@pytest.fixture(scope="session")
def snapshot_tariffs_data(snapshots_dir):
    """Данные из снепшота"""
    snapshot_path = snapshots_dir / "tariffs_response.json"
    if not snapshot_path.exists():
        pytest.skip("Снепшот не найден. Запустите: python tests/utils/create_snapshots.py")

    with open(snapshot_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ЕДИНЫЙ СПИСОК ВСЕХ СЕКЦИЙ ДЛЯ ПАРАМЕТРИЗАЦИИ
ALL_SECTIONS = [
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


class TestAPIVsSnapshots:
    """Сравнение живых данных API со снепшотами"""

    def test_section_count_match(self, tariffs_data, snapshot_tariffs_data):
        """Тест что количество секций совпадает"""
        api_sections = get_all_sections(tariffs_data)
        snapshot_sections = get_all_sections(snapshot_tariffs_data)

        assert len(api_sections) == len(snapshot_sections), \
            f"Количество секций не совпадает: API={len(api_sections)}, снепшот={len(snapshot_sections)}"

        print(f"✅ Количество секций совпадает: {len(api_sections)}")

    def test_section_names_match(self, tariffs_data, snapshot_tariffs_data):
        """Тест что названия секций совпадают"""
        api_sections = get_all_sections(tariffs_data)
        snapshot_sections = get_all_sections(snapshot_tariffs_data)

        api_names = {s["sectionName"] for s in api_sections}
        snapshot_names = {s["sectionName"] for s in snapshot_sections}

        assert api_names == snapshot_names, \
            f"Названия секций не совпадают. Разница: {api_names.symmetric_difference(snapshot_names)}"

        print(f"✅ Названия секций совпадают: {len(api_names)} секций")


@pytest.mark.parametrize("section_name", ALL_SECTIONS)
def test_section_exists_in_both(section_name, tariffs_data, snapshot_tariffs_data):
    """Параметризованный тест что секция существует и в API и в снепшоте"""
    api_section = find_section_by_name(tariffs_data, section_name)
    snapshot_section = find_section_by_name(snapshot_tariffs_data, section_name)

    assert api_section is not None, f"Секция '{section_name}' не найдена в API"
    assert snapshot_section is not None, f"Секция '{section_name}' не найдена в снепшоте"

    print(f"✅ Секция '{section_name}' существует в обоих источниках")


@pytest.mark.parametrize("section_name", ALL_SECTIONS)
def test_section_tariff_count_match(section_name, tariffs_data, snapshot_tariffs_data):
    """Параметризованный тест количества тарифов в секциях"""
    api_section = find_section_by_name(tariffs_data, section_name)
    snapshot_section = find_section_by_name(snapshot_tariffs_data, section_name)

    api_tariffs_count = len(api_section["tariffs"])
    snapshot_tariffs_count = len(snapshot_section["tariffs"])

    assert api_tariffs_count == snapshot_tariffs_count, \
        f"Количество тарифов в '{section_name}' не совпадает: API={api_tariffs_count}, снепшот={snapshot_tariffs_count}"

    print(f"✅ {section_name}: количество тарифов совпадает ({api_tariffs_count})")


@pytest.mark.parametrize("section_name", ALL_SECTIONS)
def test_tariff_names_match(section_name, tariffs_data, snapshot_tariffs_data):
    """Параметризованный тест что названия тарифов совпадают"""
    api_section = find_section_by_name(tariffs_data, section_name)
    snapshot_section = find_section_by_name(snapshot_tariffs_data, section_name)

    api_tariff_names = {t["tariffName"] for t in api_section["tariffs"]}
    snapshot_tariff_names = {t["tariffName"] for t in snapshot_section["tariffs"]}

    assert api_tariff_names == snapshot_tariff_names, \
        f"Названия тарифов в '{section_name}' не совпадают. Разница: {api_tariff_names.symmetric_difference(snapshot_tariff_names)}"

    print(f"✅ {section_name}: названия тарифов совпадают ({len(api_tariff_names)} тарифов)")


@pytest.mark.parametrize("section_name", ALL_SECTIONS)
def test_tariff_ids_consistency(section_name, tariffs_data, snapshot_tariffs_data):
    """Параметризованный тест консистентности ID тарифов"""
    api_section = find_section_by_name(tariffs_data, section_name)
    snapshot_section = find_section_by_name(snapshot_tariffs_data, section_name)

    # Создаем словари {tariff_name: tariff_id} для сравнения
    api_ids = {t["tariffName"]: t["id"] for t in api_section["tariffs"]}
    snapshot_ids = {t["tariffName"]: t["id"] for t in snapshot_section["tariffs"]}

    common_tariffs = set(api_ids.keys()) & set(snapshot_ids.keys())
    differences_found = False

    for tariff_name in common_tariffs:
        if api_ids[tariff_name] != snapshot_ids[tariff_name]:
            print(
                f"⚠️  ID тарифа '{tariff_name}' в секции '{section_name}' изменился: было {snapshot_ids[tariff_name]}, стало {api_ids[tariff_name]}")
            differences_found = True

    if not differences_found:
        print(f"✅ ID тарифов в секции '{section_name}' консистентны")


# КРИТИЧЕСКИЕ ТАРИФЫ ДЛЯ ПРОВЕРКИ ЦЕН
CRITICAL_TARIFFS_BY_SECTION = {
    "Базис для ФЛ": ["Базис для ФЛ"],
    "Базис для сотрудников": [
        "Платная лицензия (Базис) для сотрудников",
        "Платная лицензия (Базис) 12 мес КЦР"
    ]
}


@pytest.mark.parametrize("section_name", ALL_SECTIONS)
def test_critical_tariffs_prices(section_name, tariffs_data, snapshot_tariffs_data):
    """Параметризованная проверка цен критически важных тарифов"""
    if section_name not in CRITICAL_TARIFFS_BY_SECTION:
        pytest.skip(f"Нет критических тарифов для секции '{section_name}'")

    api_section = find_section_by_name(tariffs_data, section_name)
    snapshot_section = find_section_by_name(snapshot_tariffs_data, section_name)

    critical_tariffs = CRITICAL_TARIFFS_BY_SECTION[section_name]

    for tariff_name in critical_tariffs:
        api_tariff = find_tariff_by_name(api_section, tariff_name)
        snapshot_tariff = find_tariff_by_name(snapshot_section, tariff_name)

        if api_tariff and snapshot_tariff:
            assert api_tariff["price"] == snapshot_tariff["price"], \
                f"Цена тарифа '{tariff_name}' в секции '{section_name}' изменилась: было {snapshot_tariff['price']}, стало {api_tariff['price']}"

            print(f"✅ Цена '{tariff_name}' в секции '{section_name}' совпадает: {api_tariff['price']} руб.")
        else:
            print(f"⚠️  Тариф '{tariff_name}' не найден в одном из источников")


def test_api_response_structure(tariffs_data, snapshot_tariffs_data):
    """Тест общей структуры ответа API"""
    # Проверяем основные поля
    for data in [tariffs_data, snapshot_tariffs_data]:
        assert "price" in data
        assert "sections" in data["price"]
        assert isinstance(data["price"]["sections"], list)

    print("✅ Структура API ответа корректна")
