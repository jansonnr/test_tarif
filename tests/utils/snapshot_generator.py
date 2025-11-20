# tests/utils/create_snapshots.py
import json
import sys
from pathlib import Path

# Добавляем корень проекта в путь для импортов
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app_driver.wr_http_client import wrHttpClient
from config import config
from test_logic.tariff_json import get_all_sections


def create_snapshots(env="dev"):
    """Создает снепшоты в ПРАВИЛЬНОЙ директории"""
    base_url = config.get_base_url(env)
    http_client = wrHttpClient(base_url)

    # ПРАВИЛЬНЫЙ путь для снепшотов
    snapshots_dir = project_root / "test_data" / "snapshots" / env
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    print(f"🎯 Сохраняем снепшоты в: {snapshots_dir}")
    print(f"📁 Абсолютный путь: {snapshots_dir.absolute()}")

    print("🔄 Получение данных из API...")
    response = http_client.tariff()
    response.raise_for_status()
    live_data = response.json()
    print("✅ Данные получены из API")

    # Сохраняем полный ответ
    full_snapshot_path = snapshots_dir / "tariffs_response.json"
    with open(full_snapshot_path, 'w', encoding='utf-8') as f:
        json.dump(live_data, f, ensure_ascii=False, indent=2)
    print(f"✓ Полный снепшот: {full_snapshot_path.name}")

    # Сохраняем отдельные секции
    sections = get_all_sections(live_data)
    section_count = 0

    for section in sections:
        section_name = section["sectionName"]
        # Создаем имя файла
        file_name = f"section_{section_name.lower().replace(' ', '_').replace('(', '').replace(')', '')}.json"
        section_path = snapshots_dir / file_name

        with open(section_path, 'w', encoding='utf-8') as f:
            json.dump(section, f, ensure_ascii=False, indent=2)
        print(f"✓ Секция: {file_name}")
        section_count += 1

        # Проверяем что файлы создались
        created_files = list(snapshots_dir.glob("*.json"))
        print(f"\n📊 ИТОГО создано файлов: {len(created_files)}")

        print(f"✅ Все снепшоты созданы в {snapshots_dir}")
    return section_count


if __name__ == "__main__":
    try:
        count = create_snapshots("dev")
        print(f"🎉 Успешно создано {count} секций")

        # Покажем где лежат файлы
        snapshots_dir = project_root / "test_data" / "snapshots" / "dev"
        if snapshots_dir.exists():
            files = list(snapshots_dir.glob("*.json"))
            print(f"📁 Файлы находятся в: {snapshots_dir.absolute()}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback

        traceback.print_exc()