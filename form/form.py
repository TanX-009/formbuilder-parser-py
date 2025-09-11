from typing import Dict, Any, List
from .dependency import form_dep_data
from .phase import walk_phase


def walk_form(form: dict, answers: dict) -> Dict[str, Any]:
    """
    Walk an entire form and collect all answers organized by metadata.id
    """
    form_id = form.get("id", "<no-id>")
    derived_context = form_id

    # This will store the structured answers: metadata.id → list of answers
    metadata_answers: Dict[str, List[Any]] = {}

    # collect renderable phases
    renderable_phases: List[dict] = []
    for phase in form.get("phases", []):
        dep_data = form_dep_data(form, phase, derived_context, answers)
        if dep_data.get("canRender", True):
            renderable_phases.append(phase)

    # walk phases
    for i, phase in enumerate(renderable_phases):
        if not isinstance(phase, dict):
            print(f"⚠️ skipping invalid phase in form {form_id}")
            continue
        walk_phase(form, phase, derived_context, answers, metadata_answers)

    return metadata_answers
