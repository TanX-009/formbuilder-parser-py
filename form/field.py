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
    canRender: bool,
    metadata_answers: Dict[str, Any],  # dict keyed by metadata.id
    nested_answers: Dict[str, Any],
    flat_answers: Dict[str, Any],
    possible_answers: Dict[str, Any],
) -> None:
    """
    Walk a single field, handle canRender, collect answers under metadata.id, and propagate triggers.
    """
    from .section import walk_section

    field_id = field.get("id", "<no-id>")
    derived_context = f"{context}{form_context_split_str}{field_id}"

    # dependency data
    dep_data = form_dep_data(form, field, derived_context, answers)
    # if not dep_data.get("canRender", True):
    #     print(f"🔒 Field {field_id} not renderable, skipping")
    #     return

    value = answers.get(derived_context, [])
    subform_answers = get_subform_answers(derived_context, answers)

    # Metadata answers
    metadata_id = field.get("metadata", {}).get("id")
    if canRender and metadata_id:
        if value:  # regular field has answers
            if metadata_id not in metadata_answers:
                metadata_answers[metadata_id] = []
            metadata_answers[metadata_id].extend(value)
        # elif subform_answers:
        #     if metadata_id not in metadata_answers:
        #         metadata_answers[metadata_id] = {}

    # add answers
    if value and canRender and dep_data.get("canRender", True):
        # Nested answers
        if field_id not in nested_answers:
            nested_answers[field_id] = []
        nested_answers[field_id].extend(value)

        # Flat answers
        # assign if no field exists with same field_id
        if field_id not in flat_answers:
            flat_answers[field_id] = []

        #     flat_answers[field_id] = value
        # # generate a unique hash using the context if already exists
        # else:
        #     ctx_hash = str(abs(hash(context)))[:6]
        #     flat_answers[f"{field_id}::{ctx_hash}"] = value

        flat_answers[field_id].append(value)

    # Possible answers
    # only then don't create empty array of answers if the field is of type subformwtable
    if field_id not in possible_answers and field.get("type", "") != "subformwtable":
        possible_answers[field_id] = []
        if value:
            possible_answers[field_id].extend(value)

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
                    if canRender and dep_data.get("canRender", True):
                        walk_section(
                            form,
                            trig,
                            context_for_trigger,
                            answers,
                            True,
                            metadata_answers,
                            nested_answers,
                            flat_answers,
                            possible_answers,
                        )
                    else:
                        walk_section(
                            form,
                            trig,
                            context_for_trigger,
                            answers,
                            False,
                            metadata_answers,
                            nested_answers,
                            flat_answers,
                            possible_answers,
                        )

        # for possible answers
        unselected_opts = [
            opt for opt in field.get("options", []) if opt.get("value") not in value
        ]
        for opt in unselected_opts:
            for trig in opt.get("triggers", []):
                if trig.get("type") == "section":
                    walk_section(
                        form,
                        trig,
                        context_for_trigger,
                        answers,
                        False,
                        metadata_answers,
                        nested_answers,
                        flat_answers,
                        possible_answers,
                    )

    elif field_type in ["text", "textarea", "number", "password"]:
        if value and value[0] != "":
            for trig in field.get("triggers", []):
                if canRender and dep_data.get("canRender", True):
                    walk_section(
                        form,
                        trig,
                        context_for_trigger,
                        answers,
                        True,
                        metadata_answers,
                        nested_answers,
                        flat_answers,
                        possible_answers,
                    )
                else:
                    walk_section(
                        form,
                        trig,
                        context_for_trigger,
                        answers,
                        False,
                        metadata_answers,
                        nested_answers,
                        flat_answers,
                        possible_answers,
                    )
        # for possible answers
        else:
            for trig in field.get("triggers", []):
                if trig.get("type") == "section":
                    walk_section(
                        form,
                        trig,
                        context_for_trigger,
                        answers,
                        False,
                        metadata_answers,
                        nested_answers,
                        flat_answers,
                        possible_answers,
                    )

    elif field_type == "fileselect":
        files = dep_data.get("files", [])
        for f in files:
            filenames_cache[f["id"]] = f["name"]

        for _, ans_id in enumerate(value):
            filename = filenames_cache.get(str(ans_id), "")
            for trig in field.get("triggers", []):
                trig_copy = trig.copy()
                trig_copy["title"] = trig_copy.get("title", "") + filename
                trig_copy["id"] = f"{trig_copy.get('id', '')}_{ans_id}"
                if canRender and dep_data.get("canRender", True):
                    walk_section(
                        form,
                        trig_copy,
                        context_for_trigger,
                        answers,
                        True,
                        metadata_answers,
                        nested_answers,
                        flat_answers,
                        possible_answers,
                    )
                else:
                    walk_section(
                        form,
                        trig_copy,
                        context_for_trigger,
                        answers,
                        False,
                        metadata_answers,
                        nested_answers,
                        flat_answers,
                        possible_answers,
                    )
        # for possible_answers
        for trig in field.get("triggers", []):
            trig_copy = trig.copy()
            trig_copy["title"] = trig_copy.get("title", "") + "__for_possible_answers__"
            trig_copy["id"] = f"{trig_copy.get('id', '')}___for_possible_answers__"
            if trig_copy.get("type") == "section":
                walk_section(
                    form,
                    trig_copy,
                    context_for_trigger,
                    answers,
                    False,
                    metadata_answers,
                    nested_answers,
                    flat_answers,
                    possible_answers,
                )

    elif field_type == "subformwtable" and "phases" in field:
        # Only create a metadata entry if the subform itself has metadata.id
        subform_metadata_id = field.get("metadata", {}).get("id")

        if canRender:
            if subform_metadata_id not in metadata_answers:
                metadata_answers[subform_metadata_id] = {}

            # Extract all subform entry indices (n) from the answers
            subform_entry_contexts = set()
            for key in subform_answers:
                split_key = key.split(form_context_split_str)
                # The 'n' index is immediately after the derived_context parts
                n_index = split_key[len(derived_context.split(form_context_split_str))]
                subform_entry_contexts.add(n_index)

            # Walk each subform entry
            for n in sorted(subform_entry_contexts):
                entry_context = f"{derived_context}{form_context_split_str}{n}"
                # Temporary dict to hold nested metadata answers for this entry
                nested_metadata: Dict[str, Any] = {}
                nested_nested_answers: Dict[str, Any] = {}
                nested_possible_answers: Dict[str, Any] = {}

                from .phase import walk_phase

                for phase in field["phases"]:
                    walk_phase(
                        form,
                        phase,
                        entry_context,
                        answers,
                        True,
                        nested_metadata,
                        nested_nested_answers,
                        flat_answers,
                        nested_possible_answers,
                    )

                # Only append if any nested field has metadata answers
                if canRender and dep_data.get("canRender", True):
                    if nested_metadata:
                        metadata_answers[subform_metadata_id][n] = nested_metadata
                    if nested_nested_answers:
                        nested_answers[n] = nested_nested_answers
                if nested_possible_answers:
                    possible_answers[n] = nested_possible_answers

        else:
            # for possible answers
            nested_possible_answers: Dict[str, Any] = {}
            from .phase import walk_phase

            entry_context = (
                f"{derived_context}{form_context_split_str}__for_possible_answers__"
            )
            for phase in field["phases"]:
                walk_phase(
                    form,
                    phase,
                    entry_context,
                    answers,
                    False,
                    metadata_answers,
                    nested_answers,
                    flat_answers,
                    nested_possible_answers,
                )

            if nested_possible_answers:
                possible_answers["__uuid_for_possible_answers__"] = (
                    nested_possible_answers
                )
