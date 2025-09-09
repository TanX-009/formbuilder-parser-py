from typing import List
from .phase import walk_phase
from .constant import form_context_split_str


def walk_form(form: dict, answers: dict) -> None:
    from .dependency import form_dep_data

    form_id = form.get("id", "<no-id>")
    derived_context = form_id

    # collect renderable phases
    renderable_phases: List[dict] = []
    for phase in form.get("phases", []):
        dep_data = form_dep_data(form, phase, derived_context, answers)
        if dep_data["canRender"]:
            renderable_phases.append(phase)

    # walk phases
    for i, phase in enumerate(renderable_phases):
        if not isinstance(phase, dict):
            print(f"⚠️ skipping invalid phase in form {form_id}")
            continue
        walk_phase(form, phase, derived_context, answers)
