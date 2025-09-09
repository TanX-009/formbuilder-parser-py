from typing import Dict
from .constant import form_context_split_str
from .dependency import form_dep_data

# Cache for file id → filename
filenames_cache: Dict[str, str] = {}


def walk_field(form: dict, field: dict, context: str, answers: dict) -> None:
    """
    Walk a single field, handle canRender, and propagate triggers as nested sections immediately.
    """
    from .section import walk_section

    field_id = field.get("id", "<no-id>")
    derived_context = f"{context}{form_context_split_str}{field_id}"

    # dependency data
    dep_data = form_dep_data(form, field, derived_context, answers)
    if not dep_data.get("canRender", True):
        print(f"🔒 Field {field_id} not renderable, skipping")
        return

    # field answers
    value = answers.get(derived_context, [])

    field_type = field.get("type")

    # print(f"{derived_context} :: type={field_type} :: answers={value}")
    print(f"{field_id}::{field_type}={value}")

    context_for_trigger = f"{context}"
    # Handle triggers based on field type
    if field_type in [
        "radio",
        "dropdown-single-select",
        "checkbox",
        "dropdown-multi-select",
    ]:
        selected_opts = [
            opt
            for opt in field.get("options", [])
            for sel in value
            if sel == opt.get("value")
        ]
        for opt in selected_opts:
            for trig in opt.get("triggers", []):
                if trig.get("type") == "section":
                    walk_section(form, trig, context_for_trigger, answers)

    elif field_type in ["text", "textarea", "number", "password"]:
        if value and value[0] != "":
            for trig in field.get("triggers", []):
                if trig.get("type") == "section":
                    walk_section(form, trig, context_for_trigger, answers)

    elif field_type == "fileselect":
        files = dep_data.get("files", [])
        filenames_cache = {f["id"]: f["name"] for f in files}

        for i, ans_id in enumerate(value):
            filename = filenames_cache.get(str(ans_id), "")
            for trig in field.get("triggers", []):
                trig_copy = trig.copy()
                trig_copy["title"] = trig_copy.get("title", "") + filename
                trig_copy["id"] = f"{trig_copy.get('id', '')}_{ans_id}"
                if trig_copy.get("type") == "section":
                    walk_section(form, trig_copy, context_for_trigger, answers)

    else:
        # other types (mirror, mapper, etc.) → no triggers
        pass
