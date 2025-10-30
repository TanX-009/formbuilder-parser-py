import json
from typing import Any, List

# -----------------------------
# Stable hash functions
# -----------------------------


def stable_stringify(obj: Any) -> str:
    """Stable JSON stringify — same object → same string across runs (sorted keys)."""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return json.dumps(obj, ensure_ascii=False)

    if isinstance(obj, list):
        return "[" + ",".join(stable_stringify(item) for item in obj) + "]"

    if isinstance(obj, dict):
        keys = sorted(obj.keys())
        inner = ",".join(
            json.dumps(k, ensure_ascii=False) + ":" + stable_stringify(obj[k])
            for k in keys
        )
        return "{" + inner + "}"

    # fallback for non-JSON-serializable types
    return json.dumps(str(obj), ensure_ascii=False)


def fast_hash(obj: Any) -> str:
    """
    Deterministic fast hash for any JSON-serializable object.
    Produces a short, stable 32-bit hex string (like JS version).
    """
    s = stable_stringify(obj)
    h = 0
    for ch in s:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return format(h, "08x")


# -----------------------------
# Form answer type helpers
# -----------------------------


def is_file_data(v) -> bool:
    """Check if value is a TFormAnswerFileData-like object."""
    return isinstance(v, dict) and "id" in v


def is_file_data_array(v) -> bool:
    """Check if all elements in array are TFormAnswerFileData-like."""
    return len(v) > 0 and all(is_file_data(item) for item in v)


def are_arrays_equal(a: List[Any], b: List[Any]) -> bool:
    """Check shallow equality between two arrays/lists."""
    if len(a) != len(b):
        return False
    return all(x == y for x, y in zip(a, b))


def has_answer(answers: List[Any], value: dict) -> bool:
    """
    Checks if the list of TFormAnswer contains the required answer.
    Mirrors the TS logic exactly.
    """
    for ans in answers:
        if is_file_data(ans) and is_file_data(value):
            if ans.get("id") == value.get("id"):
                return True
        elif isinstance(ans, list) and isinstance(value, list):
            if are_arrays_equal(ans, value):
                return True
        elif ans == value:
            return True

    return False
