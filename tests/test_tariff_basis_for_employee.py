from app_driver.wr_http_client import wrHttpClien
from test_logic.tariff_json import get_section_by_name
from config import API_BASE_URL

def test_validate_basis_employees_section():
    #Arrange
    client = wrHttpClien(API_BASE_URL)
    tariff_selection_name = "Базис для сотрудников"
    #Act
    response = client.tariff()
    data = response.json()
    #Assert
    assert response.status_code == 200
    """Получение имени тарифа и проверка его наименования"""
    section = get_section_by_name(data,tariff_selection_name)
    assert section["sectionName"] == tariff_selection_name
        #Добавить проверку так же на название в тарифе
    section_limits = section['limits']

    expected_limit = {
        "id": "c9a7f64e-bef1-431a-8cd4-f685d8e245a1",
        "name": "Список доступных криптопровайдеров",
        "value": "[ 9, 11, 17 ]"
    }
    actual_limit = section_limits[0]
    assert actual_limit['id'] == expected_limit['id']
    assert actual_limit['name'] == expected_limit['name']
    assert actual_limit['value'] == expected_limit['value']
    return section


def test_validate_basis_for_employees_tariff():
    """Проверка тарифа 'Платная лицензия (Базис) для сотрудников'"""

    section = test_validate_basis_employees_section()

    # Находим основной тариф
    basis_tariff = None
    for tariff in section['tariffs']:
        if tariff.get('tariffName') == 'Платная лицензия (Базис) для сотрудников':
            basis_tariff = tariff
            break

    assert basis_tariff is not None, "Тариф 'Платная лицензия (Базис) для сотрудников' не найден"

    # Проверка основных полей тарифа
    assert basis_tariff['id'] == 'f5c2ec40-b5d9-46c5-a205-8f85557b63cf'
    assert basis_tariff['tariffId'] == 'f8bf1b70-d04b-4cb0-ab45-1340195b225c'
    assert basis_tariff['tariffType'] == 'Основная лицензия'
    assert basis_tariff['price'] == 2500
    assert basis_tariff['display'] == True

    # Проверка note
    assert "квалифицированный сертификат электронной подписи" in basis_tariff['note']
    assert "юридически значимый защищенный электронный документооборот" in basis_tariff['note']

    # Проверка limits тарифа
    tariff_limits = basis_tariff['limits']
    assert tariff_limits[0]['name'] == 'Список доступных криптопровайдеров'
    assert tariff_limits[0]['value'] == '[ 9, 11, 17 ]'

    # Проверка templates
    templates = basis_tariff['templates']

    template = templates[0]
    assert template['name'] == 'Квалифицированный'
    assert template['isUnstructuredNameUsed'] == False

    # Проверка CAS
    cas = template['cas']

    ca = cas[0]
    assert ca['name'] == 'ЗАО "Калуга Астрал" КриптоПро Тест'
    assert ca['isDefault'] == True
    assert ca['isFns'] == False
    assert ca['isRoseltorg'] == False

    # Проверка CA templates
    ca_templates = ca['caTemplates']

    # Первый CA template (Специализированный)
    template1 = ca_templates[0]
    assert template1['type'] == 'Специализированный'
    assert template1['oid'] == '1.2.643.2.2.50.1.9.3311484.2853914.11814819.12678195.64412.45518'
    assert template1['validity'] == 1
    assert template1['validityUnitId'] == 3
    assert template1['isCryptoProTemplate'] == False
    assert template1['isDefault'] == True

    # Второй CA template (Лицензия КриптоПро)
    template2 = ca_templates[1]
    assert template2['type'] == 'Лицензия КриптоПро в структуре сертификата'
    assert template2['oid'] == '1.2.643.2.2.50.1.9.8461984.13190941.10568297.9743651.18877.43432'
    assert template2['validity'] == 1
    assert template2['validityUnitId'] == 3
    assert template2['isCryptoProTemplate'] == True
    assert template2['isDefault'] == False

    # Проверка OIDs
    assert template['oids'] == []
    assert basis_tariff['oids'] == []

    # Проверка additionalDocuments
    assert basis_tariff['additionalDocuments'] == []

    # Проверка attributes
    attributes = basis_tariff['attributes']

    attribute = attributes[0]
    assert attribute['attributeGuid'] == 'bea894d6-d02c-4858-9bed-1ffd155a4716'
    assert attribute['attributeName'] == 'Сертификат КЭП'
    assert attribute['number'] == 1
    assert attribute['validity'] == 1
    assert attribute['validityUnitId'] == 3

    return basis_tariff


def test_validate_basis_12_months_kcr_tariff():
    """Проверка тарифа 'Платная лицензия (Базис) 12 мес КЦР'"""

    section = test_validate_basis_employees_section()

    # Находим тариф
    kcr_tariff = None
    for tariff in section['tariffs']:
        if tariff.get('tariffName') == 'Платная лицензия (Базис) 12 мес КЦР':
            kcr_tariff = tariff
            break

    assert kcr_tariff is not None, "Тариф 'Платная лицензия (Базис) 12 мес КЦР' не найден"

    # Проверка основных полей
    assert kcr_tariff['id'] == 'd5b4c856-b89f-4b5e-8cb5-ecac0712cf68'
    assert kcr_tariff['tariffId'] == 'f684aa8a-50cd-4ade-a1eb-0b42f240f3ad'
    assert kcr_tariff['tariffType'] == 'Основная лицензия'
    assert kcr_tariff['price'] == 2000
    assert kcr_tariff['display'] == True

    # Проверка note
    assert "квалифицированный сертификат электронной подписи" in kcr_tariff['note']

    # Проверка limits
    tariff_limits = kcr_tariff['limits']

    limit_names = [limit['name'] for limit in tariff_limits]
    assert 'Список доступных криптопровайдеров' in limit_names
    assert 'Только КЦР' in limit_names

    # Проверка криптопровайдеров
    crypto_limit = next(limit for limit in tariff_limits if 'криптопровайдер' in limit['name'])
    assert crypto_limit['value'] == '[ 9, 11, 17 ]'

    # Проверка templates
    templates = kcr_tariff['templates']

    template = templates[0]
    assert template['name'] == 'Квалифицированный'

    # Проверка CAS
    cas = template['cas']

    ca = cas[0]
    assert ca['name'] == 'ЗАО "Калуга Астрал" КриптоПро Тест'

    # Проверка CA templates
    ca_templates = ca['caTemplates']

    ca_template = ca_templates[0]
    assert ca_template['type'] == 'Лицензия КриптоПро в структуре сертификата'
    assert ca_template['oid'] == '1.2.643.2.2.50.1.9.12381161.765081.12535804.5723926.53976.38714'
    assert ca_template['validity'] == 15
    assert ca_template['validityUnitId'] == 1
    assert ca_template['isCryptoProTemplate'] == True
    assert ca_template['isDefault'] == False

    # Проверка attributes
    attributes = kcr_tariff['attributes']

    attribute = attributes[0]
    assert attribute['attributeGuid'] == 'bea894d6-d02c-4858-9bed-1ffd155a4716'
    assert attribute['attributeName'] == 'Сертификат КЭП'
    assert attribute['number'] == 1
    assert attribute['validity'] == 1
    assert attribute['validityUnitId'] == 3

    print("✓ Все атрибуты тарифа 'Платная лицензия (Базис) 12 мес КЦР' проверены успешно")
    return kcr_tariff


def validate_disclosure_system_tariff():
    """Проверка тарифа 'Расширение \"Системы раскрытия информации\"'"""

    section = test_validate_basis_employees_section()

    # Находим тариф
    disclosure_tariff = None
    for tariff in section['tariffs']:
        if tariff.get('tariffName') == 'Расширение "Системы раскрытия информации"':
            disclosure_tariff = tariff
            break

    assert disclosure_tariff is not None, "Тариф 'Расширение \"Системы раскрытия информации\"' не найден"

    # Проверка основных полей
    assert disclosure_tariff['id'] == 'ae239408-45da-4d87-ae8f-71eb812317b7'
    assert disclosure_tariff['tariffId'] == 'a7b7a2a6-c3e0-4f49-a746-5ca8e322311e'
    assert disclosure_tariff['tariffType'] == 'Расширение лицензии'
    assert disclosure_tariff['price'] == 500
    assert disclosure_tariff['display'] == True

    # Проверка note
    assert "Интерфакс, СКРИН, АЗИПИ, AK&M, ПРАЙМ" in disclosure_tariff['note']

    # Проверка limits
    tariff_limits = disclosure_tariff['limits']
    assert tariff_limits[0]['name'] == 'Список доступных криптопровайдеров'
    assert tariff_limits[0]['value'] == '[ 9, 11 ]'

    # Проверка OIDs
    oids = disclosure_tariff['oids']

    oid_values = [oid['value'] for oid in oids]
    expected_oids = [
        "1.2.643.6.44.1.1.1",
        "1.2.643.6.45.1.1.1",
        "1.2.643.6.42.5.5.5",
        "1.2.643.6.41.1.1.1",
        "1.2.643.6.40.1"
    ]

    for expected_oid in expected_oids:
        assert expected_oid in oid_values, f"OID {expected_oid} не найден"

    # Проверка additionalDocuments
    assert disclosure_tariff['additionalDocuments'] == []

    # Проверка attributes - ОСНОВНАЯ ПРОВЕРКА!
    attributes = disclosure_tariff['attributes']

    expected_attributes = [
        {"attributeGuid": "b23e05e4-4329-43e9-b40b-5ddb6114cfa0", "attributeName": "АЗИПИ", "number": 1},
        {"attributeGuid": "a2d60c7f-5dc4-4c5c-8789-cf298ddf6570", "attributeName": "AK&M", "number": 1},
        {"attributeGuid": "d6363a82-273d-4214-aa84-7355e35d682b", "attributeName": "ПРАЙМ", "number": 1},
        {"attributeGuid": "8628474e-1928-4373-b74b-f03a3a5b53a4", "attributeName": "Интерфакс", "number": 1},
        {"attributeGuid": "63913cc7-db23-4ecf-a4d3-f7542ac7097d", "attributeName": "СКРИН", "number": 1}
    ]

    for expected_attr in expected_attributes:
        found = False
        for actual_attr in attributes:
            if actual_attr['attributeGuid'] == expected_attr['attributeGuid']:
                assert actual_attr['attributeName'] == expected_attr['attributeName']
                assert actual_attr['number'] == expected_attr['number']
                found = True
                break
        assert found, f"Attribute {expected_attr['attributeName']} not found"
    return disclosure_tariff