# tests/test_find_prod_files.py
import pytest
import json
from pathlib import Path
from test_logic.tariff_json import find_section_by_name, get_all_sections


def test_find_actual_prod_files(snapshots_dir, tariffs_data):
    """Находит какие файлы на самом деле есть в PROD"""

    print(f"\n🔍 ПОИСК ФАЙЛОВ В PROD:")
    print("=" * 70)

    # Все файлы в папке PROD
    all_files = list(snapshots_dir.glob("*.json"))
    section_files = [f for f in all_files if f.name.startswith("section_")]

    print(f"📁 Всего файлов секций: {len(section_files)}")
    print("=" * 70)

    for file_path in section_files:
        filename = file_path.name
        # Извлекаем название из имени файла
        section_name_from_file = filename.replace("section_", "").replace(".json", "").replace("_", " ")

        print(f"📄 {filename}")
        print(f"   -> Из файла: '{section_name_from_file}'")

        # Пробуем найти соответствие в API
        with open(file_path, 'r', encoding='utf-8') as f:
            file_data = json.load(f)

        file_tariffs = len(file_data.get('tariffs', []))
        print(f"   📊 Тарифов в файле: {file_tariffs}")

        # Ищем похожие секции в API
        api_sections = get_all_sections(tariffs_data)
        matches = []

        for api_section in api_sections:
            api_name = api_section["sectionName"]
            api_tariffs = len(api_section.get('tariffs', []))

            # Если совпадает количество тарифов - вероятно это та же секция
            if api_tariffs == file_tariffs:
                matches.append((api_name, api_tariffs))

        if matches:
            print(f"   🔍 Возможные соответствия в API:")
            for api_name, api_tariffs in matches:
                print(f"      - {api_name} ({api_tariffs} тарифов)")
        else:
            print(f"   ❌ Нет соответствий в API")

        print()


def test_create_correct_prod_mapping(snapshots_dir, tariffs_data):
    """Создает правильный маппинг для PROD на основе фактических файлов"""

    print(f"\n🔍 СОЗДАНИЕ ПРАВИЛЬНОГО МАППИНГА ДЛЯ PROD:")
    print("=" * 70)

    # Все файлы в папке PROD
    section_files = list(snapshots_dir.glob("section_*.json"))

    correct_mapping = {}

    for file_path in section_files:
        filename = file_path.name

        with open(file_path, 'r', encoding='utf-8') as f:
            file_data = json.load(f)

        file_tariffs = len(file_data.get('tariffs', []))

        # Ищем секцию в API с таким же количеством тарифов
        api_sections = get_all_sections(tariffs_data)
        best_match = None

        for api_section in api_sections:
            api_name = api_section["sectionName"]
            api_tariffs = len(api_section.get('tariffs', []))

            if api_tariffs == file_tariffs:
                best_match = api_name
                break

        if best_match:
            correct_mapping[filename] = best_match
            print(f"✅ {filename} -> {best_match} ({file_tariffs} тарифов)")
        else:
            print(f"❌ {filename}: не найдено соответствие в API")

    print("=" * 70)
    print(f"📋 Правильный маппинг для PROD:")
    print("SECTION_MAPPINGS_PROD = {")
    for filename, api_name in sorted(correct_mapping.items()):
        print(f'    "{filename}": "{api_name}",')
    print("}")


def test_check_specific_prod_sections(snapshots_dir, tariffs_data):
    """Проверяем конкретные проблемные секции PROD"""

    print(f"\n🔍 ПРОВЕРКА ПРОБЛЕМНЫХ СЕКЦИЙ PROD:")
    print("=" * 70)

    # Секции которые есть в API но файлы не найдены
    problem_cases = [
        ("Бизнес", "section_бизнес.json"),
        ("Перевыпуск", "section_перевыпуск_ац.json"),
        ("Перевыпуск (Универсальный)", "section_перевыпуск_ац_универсальный.json"),
        ("СМЭВ УЛ+ИС", "section_смэв_ул_ис.json")
    ]

    for api_section_name, expected_filename in problem_cases:
        api_section = find_section_by_name(tariffs_data, api_section_name)
        file_path = snapshots_dir / expected_filename

        if api_section:
            api_tariffs = len(api_section.get('tariffs', []))
            print(f"📊 API: {api_section_name} ({api_tariffs} тарифов)")

            if file_path.exists():
                print(f"✅ Файл: {expected_filename} - СУЩЕСТВУЕТ")
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                file_tariffs = len(file_data.get('tariffs', []))
                print(f"   📊 Тарифов в файле: {file_tariffs}")
            else:
                print(f"❌ Файл: {expected_filename} - НЕ СУЩЕСТВУЕТ")

                # Ищем файл с таким же количеством тарифов
                matching_files = []
                for f in snapshots_dir.glob("section_*.json"):
                    with open(f, 'r', encoding='utf-8') as file:
                        f_data = json.load(file)
                    f_tariffs = len(f_data.get('tariffs', []))
                    if f_tariffs == api_tariffs:
                        matching_files.append((f.name, f_tariffs))

                if matching_files:
                    print(f"   🔍 Файлы с {api_tariffs} тарифами:")
                    for fname, ftariffs in matching_files:
                        print(f"      - {fname}")
        print()