from typing import Dict, Any, List, Tuple
from .dependency import form_dep_data
from .phase import walk_phase


def walk_form(
    form: dict, answers: dict
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Walk an entire form and collect all answers organized by metadata.id
    """
    form_id = form.get("id", "<no-id>")
    derived_context = form_id

    # This will store the structured answers: metadata.id → list of answers
    metadata_answers: Dict[str, List[Any]] = {}
    nested_answers: Dict[str, Any] = {}
    flat_answers: Dict[str, Any] = {}
    possible_answers: Dict[str, Any] = {}

    phases = form.get("phases", [])

    # collect renderable phases
    for phase in phases:
        dep_data = form_dep_data(form, phase, derived_context, answers)
        if not isinstance(phase, dict):
            print(f"⚠️ skipping invalid phase in form {form_id}")
            continue
        if dep_data.get("canRender", True):
            walk_phase(
                form,
                phase,
                derived_context,
                answers,
                True,
                metadata_answers,
                nested_answers,
                flat_answers,
                possible_answers,
            )
        else:
            walk_phase(
                form,
                phase,
                derived_context,
                answers,
                False,
                metadata_answers,
                nested_answers,
                flat_answers,
                possible_answers,
            )

    return metadata_answers, nested_answers, flat_answers, possible_answers
