import json
from pathlib import Path
from test_logic.tariff_json import find_section_by_name

# Маппинги для разных окружений

SECTION_MAPPINGS_1c = {
    "dev": {
        "section_Базис.json": "Базис для сотрудников",
        "section_Базис_для_ФЛфл.json": "Базис для ФЛ",
        "section_ЕГАИС.json": "ЕГАИС",
        "section_КЭП_УЦ_ФНС.json": "КЭП УЦ ФНС",
        "section_Перевыпуск.json": "Перевыпуск",
        "section_Перевыпуск_(Универсальный).json": "Перевыпуск (Универсальный)",
        "section_Платная_лицензия_(НЭП).json": "Платная лицензия (НЭП)",
        "section_Рособрнадзор.json": "Рособрнадзор",
        "section_Росреестр.json": "Росреестр",
        "section_Универсальный.json": "Универсальный",
        "section_ФТС.json": "ФТС",
        "section_СМЭВ.json": "СМЭВ",
        "section_СМЭВ_УЛ.json": "СМЭВ УЛ",
        "section_СМЭВ_УЛ+ИС.json": "СМЭВ УЛ+ИС"
    },
    "prod": {
        "section_Базис.json": "Базис для сотрудников",
        "section_Базис_для_ФЛфл.json": "Базис для ФЛ",
        "section_ЕГАИС.json": "ЕГАИС",
        "section_КЭП_УЦ_ФНС.json": "КЭП УЦ ФНС",
        "section_Перевыпуск.json": "Перевыпуск",
        "section_Перевыпуск_(Универсальный).json": "Перевыпуск (Универсальный)",
        "section_Платная_лицензия_(НЭП).json": "Платная лицензия (НЭП)",
        "section_Рособрнадзор.json": "Рособрнадзор",
        "section_Росреестр.json": "Росреестр",
        "section_Универсальный.json": "Универсальный",
        "section_ФТС.json": "ФТС",
        "section_СМЭВ.json": "СМЭВ",
        "section_СМЭВ_УЛ.json": "СМЭВ УЛ",
        "section_СМЭВ_УЛ+ИС.json": "СМЭВ УЛ+ИС"
    }
}


def save_comparison_files(api_section, file_data, section_name, env):
    """Сохраняет JSON секций для ручного сравнения при несовпадении"""
    debug_dir = Path("debug_comparison") / env
    debug_dir.mkdir(parents=True, exist_ok=True)

    # Сохраняем данные API
    api_file = debug_dir / f"{section_name}_api.json"
    with open(api_file, 'w', encoding='utf-8') as f:
        json.dump(api_section, f, ensure_ascii=False, indent=2, sort_keys=True)

    # Сохраняем данные из файла
    file_file = debug_dir / f"{section_name}_file.json"
    with open(file_file, 'w', encoding='utf-8') as f:
        json.dump(file_data, f, ensure_ascii=False, indent=2, sort_keys=True)

    return api_file, file_file


def test_section_comparison_with_debug(snapshots_dir_1c, tariffs_http_client_1c, env):
    """Сравнение секций с сохранением JSON для отладки при несовпадении"""
    mapping = SECTION_MAPPINGS_1c.get(env, {})

    print(f"\n🔍 {env.upper()}: СРАВНЕНИЕ С ОТЛАДКОЙ")
    print("=" * 70)
    print(f"📋 Проверяем {len(mapping)} секций")
    print("=" * 70)

    all_passed = True
    debug_info = []

    for filename, expected_section_name in mapping.items():
        file_path = snapshots_dir_1c / filename

        if not file_path.exists():
            print(f"❌ {filename}: ФАЙЛ НЕ СУЩЕСТВУЕТ")
            all_passed = False
            continue

        # Загружаем данные из файла
        with open(file_path, 'r', encoding='utf-8') as f:
            file_data = json.load(f)

        # Ищем секцию в API
        tariffs_http_client_response = tariffs_http_client_1c
        assert tariffs_http_client_response.status_code == 200
        tariffs_data = tariffs_http_client_response.json()
        api_section = find_section_by_name(tariffs_data, expected_section_name)

        if not api_section:
            print(f"❌ {filename}: СЕКЦИЯ '{expected_section_name}' НЕ НАЙДЕНА В API")
            all_passed = False
            continue

        # Сравниваем
        if api_section == file_data:
            tariffs_count = len(api_section.get('tariffs', []))
            print(f"✅ {filename}: СОВПАДАЕТ ({tariffs_count} тарифов)")
        else:
            file_tariffs = len(file_data.get('tariffs', []))
            api_tariffs = len(api_section.get('tariffs', []))
            print(f"❌ {filename}: НЕ СОВПАДАЕТ С '{expected_section_name}'")
            print(f"   Файл: {file_tariffs} тарифов, API: {api_tariffs} тарифов")

            # Сохраняем JSON для ручного сравнения
            api_file, file_file = save_comparison_files(api_section, file_data, expected_section_name, env)
            debug_info.append((expected_section_name, api_file, file_file))

            print(f"   💾 Сохранены файлы для сравнения:")
            print(f"      API:   {api_file}")
            print(f"      Файл: {file_file}")

            all_passed = False

    print("=" * 70)


    assert all_passed, f"НЕ ВСЕ СЕКЦИИ СОВПАДАЮТ В {env.upper()}. Проверьте debug_comparison/{env}/"

