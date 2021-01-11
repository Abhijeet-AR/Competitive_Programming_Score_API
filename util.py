def get_safe_nested_key(keys, dictionary):
    if not isinstance(dictionary, dict):
        return None
    if isinstance(keys, str):
        return dictionary.get(keys)
    if isinstance(keys, list):
        if len(keys) == 1:
            return dictionary.get(keys[0])
        if len(keys) > 1:
            return get_safe_nested_key(keys[1:], dictionary.get(keys[0]))
        return None
    return None


if __name__ == '__main__':
    assert get_safe_nested_key(['a', 'b', 'c'], {"a": {"b": {"c": "C"}}}) == "C"
    assert get_safe_nested_key(['a', 'b', 'c'], {"a": "A", "b": "B", "c": "C"}) is None
