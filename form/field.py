from typing import Dict, Any

from form.answer import get_subform_answers
from .constant import form_context_split_str
from .dependency import form_dep_data

# Cache for file id → filename
filenames_cache: Dict[str, str] = {}


def walk_field(
    form: dict,
    field: dict,
    context: str,
    answers: dict,
    metadata_answers: Dict[str, Any],  # dict keyed by metadata.id
) -> None:
    """
    Walk a single field, handle canRender, collect answers under metadata.id, and propagate triggers.
    """
    from .section import walk_section

    field_id = field.get("id", "<no-id>")
    derived_context = f"{context}{form_context_split_str}{field_id}"

    # dependency data
    dep_data = form_dep_data(form, field, derived_context, answers)
    if not dep_data.get("canRender", True):
        print(f"🔒 Field {field_id} not renderable, skipping")
        return

    value = answers.get(derived_context, [])
    subform_answers = get_subform_answers(derived_context, answers)
    # Only store answers if the field has metadata.id
    metadata_id = field.get("metadata", {}).get("id")
    # print(f"{derived_context}-----{ metadata_id }--------{value}")
    if metadata_id:
        if value:  # regular field has answers
            if metadata_id not in metadata_answers:
                metadata_answers[metadata_id] = []
            metadata_answers[metadata_id].extend(value)
        elif subform_answers:
            if metadata_id not in metadata_answers:
                metadata_answers[metadata_id] = {}

    field_type = field.get("type")
    context_for_trigger = f"{context}"

    # Handle triggers
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
                    walk_section(
                        form, trig, context_for_trigger, answers, metadata_answers
                    )

    elif field_type in ["text", "textarea", "number", "password"]:
        if value and value[0] != "":
            for trig in field.get("triggers", []):
                if trig.get("type") == "section":
                    walk_section(
                        form, trig, context_for_trigger, answers, metadata_answers
                    )

    elif field_type == "fileselect":
        files = dep_data.get("files", [])
        for f in files:
            filenames_cache[f["id"]] = f["name"]

        for i, ans_id in enumerate(value):
            filename = filenames_cache.get(str(ans_id), "")
            for trig in field.get("triggers", []):
                trig_copy = trig.copy()
                trig_copy["title"] = trig_copy.get("title", "") + filename
                trig_copy["id"] = f"{trig_copy.get('id', '')}_{ans_id}"
                if trig_copy.get("type") == "section":
                    walk_section(
                        form, trig_copy, context_for_trigger, answers, metadata_answers
                    )

    elif field_type == "subformwtable" and "phases" in field:
        # Only create a metadata entry if the subform itself has metadata.id
        subform_metadata_id = field.get("metadata", {}).get("id")
        if not subform_metadata_id:
            return  # no metadata, skip storing answers

        if subform_metadata_id not in metadata_answers:
            metadata_answers[subform_metadata_id] = {}

        # Extract all subform entry indices (n) from the answers
        subform_entry_contexts = set()
        for key in get_subform_answers(derived_context, answers):
            split_key = key.split(form_context_split_str)
            # The 'n' index is immediately after the derived_context parts
            n_index = split_key[len(derived_context.split(form_context_split_str))]
            subform_entry_contexts.add(n_index)

        # Walk each subform entry
        for n in sorted(subform_entry_contexts):
            entry_context = f"{derived_context}{form_context_split_str}{n}"
            # Temporary dict to hold nested metadata answers for this entry
            nested_metadata: Dict[str, Any] = {}

            from .phase import walk_phase

            for phase in field["phases"]:
                walk_phase(form, phase, entry_context, answers, nested_metadata)

            # Only append if any nested field has metadata answers
            if nested_metadata:
                metadata_answers[subform_metadata_id][n] = nested_metadata
