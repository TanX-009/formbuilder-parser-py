from typing import Any, List, Dict


def is_file_data(v: Any) -> bool:
    """
    Checks if a value is a file data object (TFormAnswerFileData).

    Args:
        v: The value to check.

    Returns:
        True if the value is a dict with an 'id' key.
    """
    return isinstance(v, dict) and "id" in v


def is_file_data_array(v: List[Any]) -> bool:
    """
    Checks if all values in the list are file data objects.

    Args:
        v: List of values.

    Returns:
        True if every element is a file data object.
    """
    return len(v) > 0 and all(is_file_data(item) for item in v)


def stable_stringify(obj) -> str:
    """
    Deterministic stringification of a JSON-serializable object.
    - Sorts dict keys
    - Preserves arrays order
    """
    if obj is None or not isinstance(obj, (dict, list)):
        import json

        return json.dumps(obj)

    if isinstance(obj, list):
        return "[" + ",".join(stable_stringify(x) for x in obj) + "]"

    # It's a dict
    keys = sorted(obj.keys())
    items = []
    for k in keys:
        items.append(f"{stable_stringify(k)}:{stable_stringify(obj[k])}")
    return "{" + ",".join(items) + "}"


def fast_hash(obj) -> str:
    """
    Deterministic 32-bit hash of a JSON-serializable object.
    Returns hex string.
    """
    s = stable_stringify(obj)
    hash_value = 0
    for c in s:
        hash_value = (hash_value * 31 + ord(c)) & 0xFFFFFFFF  # emulate >>> 0
    return format(hash_value, "x")
