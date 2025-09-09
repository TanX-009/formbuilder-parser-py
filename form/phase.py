from .section import walk_section
from .constant import form_context_split_str


def walk_phase(form: dict, phase: dict, context: str, answers: dict) -> None:
    from .dependency import form_dep_data

    phase_id = phase.get("id", "<no-id>")
    derived_context = f"{context}{form_context_split_str}{phase_id}"
    # print(derived_context)

    sections = phase.get("sections", [])
    if not isinstance(sections, list):
        print(f"⚠️ sections missing or not a list in phase {phase_id}")
        return

    for section in sections:
        if not isinstance(section, dict):
            print(f"⚠️ skipping invalid section in phase {phase_id}")
            continue

        # Evaluate section visibility
        dep_data = form_dep_data(form, section, derived_context, answers)
        if not dep_data.get("canRender", True):
            print(f"🔒 Section {section.get('id', '<no-id>')} not renderable, skipping")
            continue

        # Walk into section
        walk_section(form, section, derived_context, answers)
