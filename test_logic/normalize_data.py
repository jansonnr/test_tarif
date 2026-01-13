def normalize_json_data_simple(data):
    """Нормализует JSON данные, сортируя только тарифы по tariffId"""
    if isinstance(data, dict):
        result = {}
        for key in sorted(data.keys()):
            value = data[key]
            if key == 'tariffs' and isinstance(value, list):
                # Сортируем тарифы по tariffId
                result[key] = sorted(
                    value,
                    key=lambda x: str(x.get('tariffId', ''))
                )
            else:
                result[key] = value
        return result
    return data