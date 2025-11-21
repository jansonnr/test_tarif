from typing import Dict, List


def validate_limits(actual_limits: List[Dict], expected_limits: List[Dict]):
    """Валидирует структуру limits"""
    assert len(actual_limits) == len(expected_limits)

    for expected_limit in expected_limits:
        found = False
        for actual_limit in actual_limits:
            if actual_limit["id"] == expected_limit["id"]:
                assert actual_limit["name"] == expected_limit["name"]
                if "value" in expected_limit:
                    assert actual_limit.get("value") == expected_limit["value"]
                found = True
                break
        assert found, f"Limit {expected_limit['id']} not found"


def validate_attributes(actual_attributes: List[Dict], expected_attributes: List[Dict]):
    """Валидирует attributes тарифа"""
    assert len(actual_attributes) == len(expected_attributes)

    for i, expected_attr in enumerate(expected_attributes):
        actual_attr = actual_attributes[i]
        assert actual_attr["attributeGuid"] == expected_attr["attribute_guid"]
        assert actual_attr["attributeName"] == expected_attr["attribute_name"]

        if "number" in expected_attr:
            assert actual_attr.get("number") == expected_attr["number"]
        if "validity" in expected_attr:
            assert actual_attr.get("validity") == expected_attr["validity"]
        if "validity_unit_id" in expected_attr:
            assert actual_attr.get("validityUnitId") == expected_attr["validity_unit_id"]


def validate_tariff_basic_fields(tariff: Dict, expected: Dict):
    """Валидирует базовые поля тарифа"""
    assert tariff["id"] == expected["id"]
    assert tariff["tariffId"] == expected["tariff_id"]
    assert tariff["tariffName"] == expected["tariff_name"]
    assert tariff["tariffType"] == expected["tariff_type"]
    assert tariff["price"] == expected["price"]
    assert tariff["display"] == expected["display"]

    if "tariff_marketing_name" in expected:
        assert tariff.get("tariffMarketingName") == expected["tariff_marketing_name"]


def validate_tariff_structure(tariff: Dict):
    """Валидирует базовую структуру тарифа"""
    required_fields = ["id", "tariffId", "tariffName", "tariffType", "price", "display"]

    for field in required_fields:
        assert field in tariff, f"Missing required field: {field}"

    # Проверяем вложенные структуры
    assert isinstance(tariff.get("limits", []), list)
    assert isinstance(tariff.get("attributes", []), list)
    assert isinstance(tariff.get("templates", []), list)