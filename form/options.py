from inspect import iscoroutinefunction
from typing import Any, Callable, Dict, List, Optional
import httpx


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def get_by_path(obj: Dict[str, Any], path: Optional[List[str]]) -> Any:
    """
    Safely get a nested value from an object using a path array.
    """
    if not obj or not path:
        return None

    current: Any = obj
    for key in path:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return None
    return current


def valid_value(value: Any) -> Optional[str]:
    """
    Convert primitive values into string if valid.
    """
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return None


def construct_form_options_from_array(
    array: Any, mapping: Dict[str, Any]
) -> List[Dict[str, str]]:
    """
    Construct normalized form field options from raw array.
    """
    if not isinstance(array, list):
        return []

    options: List[Dict[str, str]] = []

    for item in array:
        if not isinstance(item, dict):
            continue

        option_id = valid_value(get_by_path(item, mapping.get("id")))
        label = valid_value(get_by_path(item, mapping.get("label")))
        value = valid_value(get_by_path(item, mapping.get("value")))
        note = (
            valid_value(get_by_path(item, mapping.get("description")))
            if mapping.get("description")
            else None
        )

        if option_id and label and value:
            opt = {
                "id": option_id,
                "label": label,
                "value": value,
            }
            if note:
                opt["note"] = note
            options.append(opt)

    return options


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------
async def get_form_options(
    url: str,
    mapping: Dict[str, Any],
    async_map: dict[str, Callable],
    *,
    debug: bool = False,
    timeout: float = 10.0,
) -> List[Dict[str, str]]:
    """
    Fetch a list of options from a remote API and normalize it
    using the provided mapping.

    - If `async_map[url]` exists, that async function is used instead
      of making an HTTP request.
    - Otherwise, falls back to an HTTP GET using httpx.

    Supports nested extraction via `mapping["prenest"]`.
    """

    # ----------------------------
    # Data fetch
    # ----------------------------
    if url in async_map:
        fetch_fn = async_map[url]

        print(f"Using async_map handler for url: {url}")
        if iscoroutinefunction(fetch_fn):
            data: Any = await fetch_fn()
        else:
            data: Any = fetch_fn()

    else:
        print(f"Fetching options via HTTP from: {url}")

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            data: Any = response.json()

    # ----------------------------
    # Debug output
    # ----------------------------
    if debug:
        print(f"Fetched data for options ({url}):\n{data}")

    # ----------------------------
    # Prenest handling
    # ----------------------------
    target_array = (
        get_by_path(data, mapping.get("prenest")) if mapping.get("prenest") else data
    )

    # ----------------------------
    # Normalize to form options
    # ----------------------------
    return construct_form_options_from_array(target_array, mapping)
