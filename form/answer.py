from collections import Counter
from typing import Any, List, Dict
from .constant import form_context_split_str

# This will be passed in from main.py
# answers: Dict[str, List[Any]] = {}


def get_subform_answers(
    context: str, answers: Dict[str, List[Any]]
) -> Dict[str, List[Any]]:
    """
    Extracts answers belonging to a specific subform context.

    Args:
        context: The subform context string (used to match against keys).
        answers: The full form answers dictionary.

    Returns:
        A dictionary of subform answers keyed by their full context path.
        Only keys that match the context exactly or start with "context + separator" are included.
    """
    result: Dict[str, List[Any]] = {}
    context_prefix = (
        context + form_context_split_str
    )  # or your actual form_context_split_str

    for key, value in answers.items():
        if key == context or key.startswith(context_prefix):
            result[key] = value

    return result


def get_form_answer(context: str, answers: Dict[str, List[Any]]) -> List[Any]:
    """
    Retrieves the answer array for a given context.
    Returns an empty list if none exist.
    """
    return answers.get(context, [])


def are_form_answers_equal(a: List[Any], b: List[Any]) -> bool:
    """
    Compares two answer lists for equality,
    ignoring order but considering duplicates.
    """
    return Counter(a) == Counter(b)
