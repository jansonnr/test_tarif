# tests/test_api_vs_snapshots.py
import pytest
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from test_logic.tariff_json import find_section_by_name, find_tariff_by_name, get_all_sections


@pytest.fixture(scope="session")
def snapshot_tariffs_data(snapshots_dir):
    """Данные из снепшота"""
    snapshot_path = snapshots_dir / "tariffs_response.json"
    if not snapshot_path.exists():
        pytest.skip("Снепшот не найден")

    with open(snapshot_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture(scope="session")
def common_sections(tariffs_data, snapshot_tariffs_data):
    """Динамический список общих секций"""
    api_sections = get_all_sections(tariffs_data)
    snapshot_sections = get_all_sections(snapshot_tariffs_data)

    api_names = {s["sectionName"] for s in api_sections}
    snapshot_names = {s["sectionName"] for s in snapshot_sections}

    common = api_names & snapshot_names

    # Выводим информацию о секциях
    print(f"\n🔍 ИНФОРМАЦИЯ О СЕКЦИЯХ:")
    print(f"📊 API секций: {len(api_names)}")
    print(f"📊 Снепшот секций: {len(snapshot_names)}")
    print(f"🎯 Общих секций для тестирования: {len(common)}")

    only_in_api = api_names - snapshot_names
    only_in_snapshot = snapshot_names - api_names

    if only_in_api:
        print(f"🆕 Только в API: {only_in_api}")
    if only_in_snapshot:
        print(f"🗑️  Только в снепшоте: {only_in_snapshot}")

    return sorted(common)


@pytest.mark.parametrize("section_name", [
    "Базис для ФЛ",
    "Базис для сотрудников",
    "Универсальный"
])
def test_critical_sections_exist(section_name, tariffs_data, snapshot_tariffs_data):
    """Тест что критические секции существуют"""
    api_section = find_section_by_name(tariffs_data, section_name)
    snapshot_section = find_section_by_name(snapshot_tariffs_data, section_name)

    assert api_section is not None
    assert snapshot_section is not None
    print(f"✅ {section_name} - существует в обоих источниках")


def test_common_sections_tariff_count(common_sections, tariffs_data, snapshot_tariffs_data):
    """Проверка количества тарифов в общих секциях"""
    for section_name in common_sections:
        api_section = find_section_by_name(tariffs_data, section_name)
        snapshot_section = find_section_by_name(snapshot_tariffs_data, section_name)

        api_count = len(api_section["tariffs"])
        snapshot_count = len(snapshot_section["tariffs"])

        assert api_count == snapshot_count, \
            f"Количество тарифов в '{section_name}' не совпадает: API={api_count}, снепшот={snapshot_count}"

        print(f"✅ {section_name}: {api_count} тарифов")


def test_common_sections_tariff_names(common_sections, tariffs_data, snapshot_tariffs_data):
    """Проверка названий тарифов в общих секциях"""
    for section_name in common_sections:
        api_section = find_section_by_name(tariffs_data, section_name)
        snapshot_section = find_section_by_name(snapshot_tariffs_data, section_name)

        api_names = {t["tariffName"] for t in api_section["tariffs"]}
        snapshot_names = {t["tariffName"] for t in snapshot_section["tariffs"]}

        assert api_names == snapshot_names, \
            f"Названия тарифов в '{section_name}' не совпадают. Разница: {api_names.symmetric_difference(snapshot_names)}"

        print(f"✅ {section_name}: названия тарифов совпадают")


def test_common_sections_tariff_ids(common_sections, tariffs_data, snapshot_tariffs_data):
    """Проверка ID тарифов в общих секциях"""
    differences_found = False

    for section_name in common_sections:
        api_section = find_section_by_name(tariffs_data, section_name)
        snapshot_section = find_section_by_name(snapshot_tariffs_data, section_name)

        api_ids = {t["tariffName"]: t["id"] for t in api_section["tariffs"]}
        snapshot_ids = {t["tariffName"]: t["id"] for t in snapshot_section["tariffs"]}

        common_tariffs = set(api_ids.keys()) & set(snapshot_ids.keys())

        for tariff_name in common_tariffs:
            if api_ids[tariff_name] != snapshot_ids[tariff_name]:
                print(
                    f"⚠️  ID тарифа '{tariff_name}' в '{section_name}' изменился: было {snapshot_ids[tariff_name]}, стало {api_ids[tariff_name]}")
                differences_found = True

        if not any(api_ids.get(name) != snapshot_ids.get(name) for name in common_tariffs):
            print(f"✅ {section_name}: ID тарифов консистентны")

    if not differences_found:
        print("🎉 Все ID тарифов совпадают!")


def test_critical_tariffs_prices(common_sections, tariffs_data, snapshot_tariffs_data):
    """Проверка цен критических тарифов"""
    # Критические тарифы для проверки цен
    CRITICAL_TARIFFS = {
        "Базис для ФЛ": ["Базис для ФЛ"],
        "Базис для сотрудников": [
            "Платная лицензия (Базис) для сотрудников",
            "Платная лицензия (Базис) 12 мес КЦР"
        ]
    }

    price_changes_found = False

    for section_name in common_sections:
        if section_name not in CRITICAL_TARIFFS:
            continue

        api_section = find_section_by_name(tariffs_data, section_name)
        snapshot_section = find_section_by_name(snapshot_tariffs_data, section_name)

        for tariff_name in CRITICAL_TARIFFS[section_name]:
            api_tariff = find_tariff_by_name(api_section, tariff_name)
            snapshot_tariff = find_tariff_by_name(snapshot_section, tariff_name)

            if api_tariff and snapshot_tariff:
                if api_tariff["price"] != snapshot_tariff["price"]:
                    print(
                        f"💰 Цена '{tariff_name}' в '{section_name}' изменилась: было {snapshot_tariff['price']}, стало {api_tariff['price']}")
                    price_changes_found = True
                else:
                    print(f"✅ {tariff_name} в {section_name}: цена {api_tariff['price']} руб. (не изменилась)")

    if not price_changes_found:
        print("🎉 Цены критических тарифов не изменились!")


def test_section_limits_structure(common_sections, tariffs_data, snapshot_tariffs_data):
    """Проверка структуры limits секций"""
    sections_with_none_limits = []
    sections_with_list_limits = []

    for section_name in common_sections:
        api_section = find_section_by_name(tariffs_data, section_name)
        snapshot_section = find_section_by_name(snapshot_tariffs_data, section_name)

        # Проверяем что limits есть в обоих
        assert "limits" in api_section
        assert "limits" in snapshot_section

        # Проверяем типы
        api_limits = api_section["limits"]
        snapshot_limits = snapshot_section["limits"]

        assert api_limits is None or isinstance(api_limits, list)
        assert snapshot_limits is None or isinstance(snapshot_limits, list)

        # Собираем статистику
        if api_limits is None:
            sections_with_none_limits.append(section_name)
        else:
            sections_with_list_limits.append(section_name)

        # Проверяем что API и снепшот согласованы
        assert (api_limits is None) == (snapshot_limits is None), \
            f"Секция '{section_name}': limits не согласованы (API: {type(api_limits)}, снепшот: {type(snapshot_limits)})"

    print(
        f"✅ Структура limits: {len(sections_with_list_limits)} секций с limits, {len(sections_with_none_limits)} секций без limits")


def test_tariff_structure(common_sections, tariffs_data, snapshot_tariffs_data):
    """Проверка структуры тарифов"""
    required_fields = ["id", "tariffId", "tariffName", "tariffType", "price", "display"]

    for section_name in common_sections:
        api_section = find_section_by_name(tariffs_data, section_name)

        for tariff in api_section["tariffs"]:
            for field in required_fields:
                assert field in tariff, f"Тариф '{tariff.get('tariffName', 'unknown')}' в секции '{section_name}' не имеет поля '{field}'"

    print("✅ Структура всех тарифов корректна")


def test_api_vs_snapshot_summary(tariffs_data, snapshot_tariffs_data):
    """Сводная информация о сравнении"""
    api_sections = get_all_sections(tariffs_data)
    snapshot_sections = get_all_sections(snapshot_tariffs_data)

    print(f"\n📊 СВОДКА СРАВНЕНИЯ API vs СНЕПШОТ:")
    print("=" * 50)
    print(f"🔸 Секций в API: {len(api_sections)}")
    print(f"🔸 Секций в снепшоте: {len(snapshot_sections)}")
    print(
        f"🔸 Общих секций: {len(set(s['sectionName'] for s in api_sections) & set(s['sectionName'] for s in snapshot_sections))}")
    print(f"🔸 Всего тарифов в API: {sum(len(s['tariffs']) for s in api_sections)}")
    print(f"🔸 Всего тарифов в снепшоте: {sum(len(s['tariffs']) for s in snapshot_sections)}")
    print("🎯 Сравнение завершено!")