from collections import Counter
from typing import Any, List, Dict

# This will be passed in from main.py
# answers: Dict[str, List[Any]] = {}


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
