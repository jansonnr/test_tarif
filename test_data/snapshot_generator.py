import json
from pathlib import Path
from config import Config
from app_driver.wr_http_client import wrHttpClient
from test_logic.tariff_json import get_all_sections


def generate_section_files_for_env(env_name: str):

    # Получаем URL для окружения
    base_url = Config.get_base_url(env_name)

    # Создаем HTTP клиент и получаем данные
    http_client = wrHttpClient(base_url)
    response = http_client.tariff_1c()
    response.raise_for_status()
    api_data = response.json()

    # Директория для сохранения
    project_root = Path(__file__).parent.parent
    snapshots_dir = project_root / "test_data" / "snapshots_1c" / env_name
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    # Сохраняем полный ответ API
    full_response_path = snapshots_dir / "tariffs_response.json"
    with open(full_response_path, 'w', encoding='utf-8') as f:
        json.dump(api_data, f, ensure_ascii=False, indent=2)

    # Получаем все секции
    all_sections = get_all_sections(api_data)

    print(f"🔍 Найдено секций в {env_name}: {len(all_sections)}")

    # Генерируем файлы для каждой секции
    sections_created = 0
    for section in all_sections:
        section_name = section.get('sectionName')
        if section_name:
            # Создаем безопасное имя файла
            safe_filename = f"section_{section_name.replace(' ', '_').replace('/', '_').replace('?', '').replace(' * ', '')}.json"
            section_file_path = snapshots_dir / safe_filename

            # Сохраняем секцию в отдельный файл
            with open(section_file_path, 'w', encoding='utf-8') as f:
                json.dump(section, f, ensure_ascii=False, indent=2)

            sections_created += 1
            print(f"📄 Создан файл: {safe_filename}")

            print(f"✅ Для окружения {env_name} создано {sections_created} файлов секций")
    return sections_created


def generate_section_files_for_both_envs():
    """Генерирует файлы секций для обоих окружений (dev и prod)"""
    print("🚀 Запуск генерации файлов секций для всех окружений...")

    total_sections = 0
    for env_name in ["dev", "prod"]:
        print(f"\n{'=' * 50}")
        print(f"🔄 Обработка окружения: {env_name}")
        print(f"📡 URL: {Config.get_base_url(env_name)}")
        print(f"📁 Директория: test_data/snapshots/{env_name}")
        print(f"{'=' * 50}")

        try:
            sections_count = generate_section_files_for_env(env_name)
            total_sections += sections_count
        except Exception as e:
            print(f"❌ Ошибка при обработке окружения {env_name}: {e}")

    print(f"\n🎉 Генерация завершена!")
    print(f"📊 Всего обработано секций: {total_sections}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Генератор снепшотов секций')
    parser.add_argument('--env', choices=['dev', 'prod', 'all'], default='all')

    args = parser.parse_args()

    if args.env == 'all':
        generate_section_files_for_both_envs()
    else:
        generate_section_files_for_env(args.env)