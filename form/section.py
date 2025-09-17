from typing import Dict, Any
from .constant import form_context_split_str
from .field import walk_field
from .dependency import form_dep_data


def walk_section(
    form: dict,
    section: dict,
    context: str,
    answers: dict,
    metadata_answers: Dict[str, Any],  # nested dict passed from phase
    nested_answers: Dict[str, Any],
    flat_answers: Dict[str, Any],
) -> None:
    """
    Walk over fields in a section and call walk_field for each renderable field.
    Handles section-level metadata nesting.
    """
    section_id = section.get("id", "<no-id>")
    derived_context = f"{context}{form_context_split_str}{section_id}"

    # Section-level metadata
    section_meta_id = section.get("metadata", {}).get("id")
    if section_meta_id:
        # Ensure a nested dict for this section inside the parent metadata dict
        if section_meta_id not in metadata_answers:
            metadata_answers[section_meta_id] = {}
        nested_metadata = metadata_answers[section_meta_id]
    else:
        nested_metadata = metadata_answers

    # Ensure a nested dict for this section
    if section_id not in nested_answers:
        nested_answers[section_id] = {}
    nested_nested_answers = nested_answers[section_id]

    fields = section.get("fields", [])
    if not isinstance(fields, list):
        print(f"⚠️ section.fields missing or not a list in section {section_id}")
        return

    for field in fields:
        if not isinstance(field, dict):
            print(f"⚠️ skipping invalid field in section {section_id}")
            continue

        dep_data = form_dep_data(form, field, derived_context, answers)
        if dep_data.get("canRender", True):
            # Pass nested_metadata so the field can add its answers under this section's metadata
            walk_field(
                form,
                field,
                derived_context,
                answers,
                nested_metadata,
                nested_nested_answers,
                flat_answers,
            )
