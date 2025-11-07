import pytest

def get_section_by_name(data, tariff_selection_name):
    """функция для поиска тарифа по имени"""
    sections = data.get('price', {}).get('sections', [])
    for section in sections:
        if section.get("sectionName") == tariff_selection_name:
            return section
    pytest.fail(f"Tariff '{tariff_selection_name}' not found")

def get_limits_in_tariff(data, tariff_selection_name, name_limits):
    """функция для поиска доступных лимитов в тарифе по имени"""
    sections = data.get('price', {}).get('sections', [])
    for section in sections:
        if section.get("sectionName") == tariff_selection_name:
            limits = section.get('limits', [])
            for limit in limits:
                if limit.get("name") == name_limits:
                    return limit.get("value")
    pytest.fail(f"Tariff '{name_limits}' not found") 