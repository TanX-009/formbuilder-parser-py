from .constant import form_context_split_str
from .field import walk_field
from .dependency import form_dep_data


def walk_section(form: dict, section: dict, context: str, answers: dict) -> None:
    """
    Walk over fields in a section and call walk_field for each renderable field.
    Triggers are handled immediately inside walk_field.
    """
    section_id = section.get("id", "<no-id>")
    derived_context = f"{context}{form_context_split_str}{section_id}"
    # print(f"SECTION CONTEXT: {derived_context}")

    fields = section.get("fields", [])
    if not isinstance(fields, list):
        print(f"⚠️ section.fields missing or not a list in section {section_id}")
        return

    for field in fields:
        if not isinstance(field, dict):
            print(f"⚠️ skipping invalid field in section {section_id}")
            continue

        # Evaluate field visibility and walk it
        dep_data = form_dep_data(form, field, derived_context, answers)
        if dep_data.get("canRender", True):
            walk_field(form, field, derived_context, answers)
