from app_driver.wr_http_client import wrHttpClien
from test_logic.tariff_json import get_section_by_name
from config import API_BASE_URL

def test_validate_basis_fl_section():
    #Arrange
    client = wrHttpClien(API_BASE_URL)
    tariff_selection_name = "Базис для ФЛ"
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
    expected_limits = [
        {"id": "dba02e4f-3a97-44d7-8b19-a0dac8e58674", "name": "Физическое лицо"},
        {"id": "19c6bf21-f5a3-49d5-818f-84944b055e55", "name": "Максимальное число расширений", "value": "3"},
        {"id": "c9a7f64e-bef1-431a-8cd4-f685d8e245a1", "name": "Список доступных криптопровайдеров",
         "value": "[ 9, 11, 17 ]"}
    ]
    for expected_limit in expected_limits:
        found = False
        for actual_limit in section_limits:
            if actual_limit['id'] == expected_limit['id']:
                assert actual_limit['name'] == expected_limit['name']
                if 'value' in expected_limit:
                    assert actual_limit['value'] == expected_limit['value']
                found = True
                break
        assert found, f"Limit {expected_limit['id']} not found"
    return section

def test_validate_basis_fl_tariff():
    """Проверка основного тарифа 'Базис для ФЛ'"""
    section = test_validate_basis_fl_section()
    tariffs = [t for t in section['tariffs'] if t]  # Фильтруем пустые

    # Находим основной тариф
    basis_tariff = None
    for tariff in tariffs:
        if tariff.get('tariffName') == 'Базис для ФЛ':
            basis_tariff = tariff
            break

    # Проверка основных полей тарифа
    assert basis_tariff['id'] == 'd2e8319c-0b70-47eb-b177-b35a8263c3f8'
    assert basis_tariff['tariffId'] == 'a211b83f-47a2-4553-b42c-8afcde6e16ea'
    assert basis_tariff['tariffType'] == 'Основная лицензия'
    assert basis_tariff['price'] == 2000
    assert basis_tariff['display'] == True

    # Проверка templates
    templates = basis_tariff['templates']

    template = templates[0]
    assert template['name'] == 'Квалифицированный'
    assert template['isUnstructuredNameUsed'] == False

    # Проверка CAS
    cas = template['cas']

    # Проверка первой CA
    ca1 = cas[0]
    assert ca1['name'] == 'ЗАО "Калуга Астрал" 833'
    assert ca1['isDefault'] == True
    assert ca1['isFns'] == False
    assert ca1['isRoseltorg'] == False
    assert ca1['caTemplates'] == []  # Пустой список

    # Проверка второй CA
    ca2 = cas[1]
    assert ca2['name'] == 'ЗАО "Калуга Астрал" КриптоПро Тест'
    assert ca2['isDefault'] == False
    assert ca2['isFns'] == False
    assert ca2['isRoseltorg'] == False

    # Проверка CA templates второй CA
    ca2_templates = ca2['caTemplates']

    # Первый CA template
    template1 = ca2_templates[0]
    assert template1['type'] == 'Лицензия КриптоПро в структуре сертификата'
    assert template1['oid'] == '1.2.643.2.2.50.1.9.8461984.13190941.10568297.9743651.18877.43432'
    assert template1['validity'] == 1
    assert template1['validityUnitId'] == 3
    assert template1['isCryptoProTemplate'] == True
    assert template1['isDefault'] == False

    # Второй CA template
    template2 = ca2_templates[1]
    assert template2['type'] == 'Специализированный'
    assert template2['oid'] == '1.2.643.2.2.50.1.9.3311484.2853914.11814819.12678195.64412.45518'
    assert template2['validity'] == 1
    assert template2['validityUnitId'] == 3
    assert template2['isCryptoProTemplate'] == False
    assert template2['isDefault'] == False

    # Проверка OIDs
    assert template['oids'] == []

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


def test_validate_plus_3_months_tariff():
    """Проверка тарифа '+3 месяца к сроку действия сертификата'"""

    section = test_validate_basis_fl_section()
    tariffs = [t for t in section['tariffs'] if t]

    # Находим тариф
    plus_3_tariff = None
    for tariff in tariffs:
        if tariff.get('tariffName') == '+3 месяца к сроку действия сертификата':
            plus_3_tariff = tariff
            break

    # Проверка основных полей
    assert plus_3_tariff['id'] == 'ff867c1d-8c43-4403-a019-9495003a9849'
    assert plus_3_tariff['tariffId'] == '57b8591f-2ef8-4777-88a3-95769b4f54b5'
    assert plus_3_tariff['tariffMarketingName'] == '+3 месяца к сроку действия сертификата'
    assert plus_3_tariff['tariffType'] == 'Расширение лицензии'
    assert plus_3_tariff['price'] == 500
    assert plus_3_tariff['display'] == True

    # Проверка attributes
    attributes = plus_3_tariff['attributes']

    attribute = attributes[0]
    assert attribute['attributeGuid'] == 'bea894d6-d02c-4858-9bed-1ffd155a4716'
    assert attribute['attributeName'] == 'Сертификат КЭП'
    assert 'number' not in attribute  # В этом тарифе нет number
    assert attribute['validity'] == 15
    assert attribute['validityUnitId'] == 1

    return plus_3_tariff

