def add_values_from_dict(target_dict: dict, update_dict: dict) -> dict:
    for key, value in update_dict.items():
        target_dict[key] = target_dict.get(key, 0) + value
    return target_dict
