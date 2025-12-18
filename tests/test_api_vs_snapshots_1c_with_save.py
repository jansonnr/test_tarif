import json
from test_logic.tariff_json import find_section_by_name
from config import config
from app_driver.wr_http_client import wrHttpClient
from test_data.selection_mapping_1c import SECTION_MAPPINGS_1c
from helper_save_difference import save_comparison_files


def test_section_comparison_with_debug():
    """Сравнение секций с сохранением JSON для отладки при несовпадении"""
    env = config.ENV
    mapping = SECTION_MAPPINGS_1c.get(env, {})

    print(f"\n🔍 {env.upper()}: СРАВНЕНИЕ С ОТЛАДКОЙ")
    print("=" * 70)
    print(f"📋 Проверяем {len(mapping)} секций")
    print("=" * 70)

    all_passed = True
    debug_info = []

    for filename, expected_section_name in mapping.items():
        file_path = config.snapshots_dir_1c / filename

        if not file_path.exists():
            print(f"❌ {filename}: ФАЙЛ НЕ СУЩЕСТВУЕТ")
            all_passed = False
            continue

        # Загружаем данные из файла
        with open(file_path, 'r', encoding='utf-8') as f:
            file_data = json.load(f)

        # Ищем секцию в API
        client = wrHttpClient()
        tariffs_http_client_response = client.tariff_1c()
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

