from typing import Dict, List, Optional


def find_section_by_name(data: Dict, section_name: str) -> Optional[Dict]:
    """Ищет секцию по имени (если структура плоская или почти плоская)"""
    all_sections = get_all_sections(data)
    for section in all_sections:
        if section.get("sectionName") == section_name:
            return section
    return None


def find_tariff_by_name(section: Dict, tariff_name: str) -> Optional[Dict]:
    """Ищет тариф по имени в секции"""
    for tariff in section.get("tariffs", []):
        if tariff.get("tariffName") == tariff_name:
            return tariff
    return None


def get_all_sections(data: Dict) -> List[Dict]:
    """Возвращает все секции из данных (включая вложенные)"""
    sections = []

    def extract_sections(sections_list):
        for section in sections_list:
            sections.append(section)
            if "sections" in section:
                extract_sections(section["sections"])

    extract_sections(data["price"]["sections"])
    return sections


def get_all_tariffs(data: Dict) -> List[Dict]:
    """Возвращает все тарифы из всех секций"""
    tariffs = []
    sections = get_all_sections(data)

    for section in sections:
        tariffs.extend(section.get("tariffs", []))

    return tariffs