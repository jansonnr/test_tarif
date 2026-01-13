from pathlib import Path
import json

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