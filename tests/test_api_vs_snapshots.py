import json
from test_logic.tariff_json import find_section_by_name
from test_logic.tariff_json import get_all_sections

# МАППИНГИ ДЛЯ ВСЕХ ОКРУЖЕНИЙ
SECTION_MAPPINGS = {
    "dev": {
        "section_базис_для_сотрудников.json": "Базис для сотрудников",
        "section_базис_для_фл.json": "Базис для ФЛ",
        "section_бизнес.json": "Бизнес",
        "section_госзаказ.json": "Госзаказ",
        "section_егаис.json": "ЕГАИС",
        "section_кэп_уц_фнс.json": "КЭП УЦ ФНС",
        "section_перевыпуск_ац.json": "Перевыпуск АЦ",
        "section_перевыпуск_ац_универсальный.json": "Перевыпуск АЦ (Универсальный)",
        "section_платная_лицензия_нэп.json": "Платная лицензия (НЭП)",
        "section_рособрнадзор.json": "Рособрнадзор",
        "section_росреестр.json": "Росреестр",
        "section_универсальный.json": "Универсальный",
        "section_фтс.json": "ФТС"
    },
    "prod": {
        "section_базис_для_сотрудников.json": "Базис для сотрудников",
        "section_базис_для_фл.json": "Базис для ФЛ",
        "section_бизнес.json": "Бизнес",
        "section_госзаказ.json": "Госзаказ",
        "section_егаис.json": "ЕГАИС",
        "section_кэп_уц_фнс.json": "КЭП УЦ ФНС",
        "section_перевыпуск.json": "Перевыпуск",
        "section_перевыпуск_универсальный.json": "Перевыпуск (Универсальный)",
        "section_платная_лицензия_нэп.json": "Платная лицензия (НЭП)",
        "section_рособрнадзор.json": "Рособрнадзор",
        "section_росреестр.json": "Росреестр",
        "section_универсальный.json": "Универсальный",
        "section_фтс.json": "ФТС",
        "section_смэв.json": "СМЭВ",
        "section_смэв_ул.json": "СМЭВ УЛ",
        "section_смэв_ул+ис.json": "СМЭВ УЛ+ИС"
    }
}


def test_exact_section_match_for_env(snapshots_dir, tariffs_http_client, env):
    """Тест для конкретного окружения: проверяем только секции из маппинга"""
    mapping = SECTION_MAPPINGS.get(env, {})

    print(f"\n🔍 {env.upper()}: ПРОВЕРКА СЕКЦИЙ ИЗ МАППИНГА")
    print(f"📋 В маппинге: {len(mapping)} секций")

    all_passed = True
    checked_sections = []
    missing_files = []

    for filename, expected_section_name in mapping.items():
        file_path = snapshots_dir / filename

        if not file_path.exists():
            missing_files.append(filename)
            continue

        # Загружаем данные из файла
        with open(file_path, 'r', encoding='utf-8') as f:
            file_data = json.load(f)

        # Ищем секцию в API
        tariffs_http_client_response = tariffs_http_client
        assert tariffs_http_client_response.status_code == 200
        tariffs_data = tariffs_http_client_response.json()
        api_section = find_section_by_name(tariffs_data, expected_section_name)

        if not api_section:
            print(f"❌ {filename}: СЕКЦИЯ '{expected_section_name}' НЕ НАЙДЕНА В API")
            all_passed = False
            continue

        # Сравниваем - ДОЛЖНЫ БЫТЬ ИДЕНТИЧНЫ
        if api_section == file_data:
            tariffs_count = len(api_section.get('tariffs', []))
            print(f"✅ {filename}: СОВПАДАЕТ ({tariffs_count} тарифов)")
            checked_sections.append(expected_section_name)
        else:
            file_tariffs = len(file_data.get('tariffs', []))
            api_tariffs = len(api_section.get('tariffs', []))
            print(f"❌ {filename}: НЕ СОВПАДАЕТ С '{expected_section_name}'")
            print(f"   Файл: {file_tariffs} тарифов, API: {api_tariffs} тарифов")
            all_passed = False

    print("=" * 70)

    # Показываем статистику
    print(f"📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
    print(f"   ✅ Проверено секций: {len(checked_sections)}")
    if missing_files:
        print(f"   ⚠️  Отсутствуют файлы: {len(missing_files)}")
        for filename in missing_files:
            print(f"      - {filename}")

    # Находим секции в API, которые не проверялись

    all_api_sections = get_all_sections(tariffs_data)
    all_api_section_names = {s["sectionName"] for s in all_api_sections}
    checked_section_names = set(checked_sections)
    unchecked_sections = all_api_section_names - checked_section_names

    if unchecked_sections:
        print(f"   🔍 Не проверялись (есть в API, но нет в маппинге): {len(unchecked_sections)}")

    assert all_passed, f"НЕ ВСЕ СЕКЦИИ СОВПАДАЮТ В {env.upper()}"


def test_show_environment_info(tariffs_http_client, env):
    """Показывает информацию о секциях в текущем окружении"""
    from test_logic.tariff_json import get_all_sections
    tariffs_http_client_response = tariffs_http_client
    assert tariffs_http_client_response.status_code == 200
    tariffs_data = tariffs_http_client_response.json()
    all_sections = get_all_sections(tariffs_data)
    mapping = SECTION_MAPPINGS.get(env, {})

    print(f"\n📊 ИНФОРМАЦИЯ ДЛЯ {env.upper()}:")
    print("=" * 60)
    print(f"📋 Секций в маппинге: {len(mapping)}")
    print(f"📊 Секций в API: {len(all_sections)}")

    # Находим пересечение
    api_section_names = {s["sectionName"] for s in all_sections}
    mapping_section_names = set(mapping.values())
    common_sections = api_section_names & mapping_section_names
    only_in_api = api_section_names - mapping_section_names
    only_in_mapping = mapping_section_names - api_section_names

    print(f"📈 Общих секций: {len(common_sections)}")
    print(f"🔍 Только в API: {len(only_in_api)}")
    print(f"📁 Только в маппинге: {len(only_in_mapping)}")
    print("=" * 60)
