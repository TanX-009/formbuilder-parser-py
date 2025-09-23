from typing import Dict, Any, Optional
from .constant import form_context_split_str
from .field import walk_field
from .dependency import form_dep_data


def walk_section(
    form: dict,
    section: dict,
    context: str,
    metadata_context: list[str],
    answers: dict,
    answersWRTMetadata: Optional[dict],
    canRender: bool,
    metadata_answers: Dict[str, Any],  # nested dict passed from phase
    nested_answers: Dict[str, Any],
    flat_answers: Dict[str, Any],
    possible_answers: Dict[str, Any],
    constructed_answers: Dict[str, Any],
) -> None:
    """
    Walk over fields in a section and call walk_field for each renderable field.
    Handles section-level metadata nesting.
    """
    section_id = section.get("id", "<no-id>")
    derived_context = f"{context}{form_context_split_str}{section_id}"
    derived_metadata_context = []
    derived_metadata_context.extend(metadata_context)

    section_meta_id = section.get("metadata", {}).get("id")

    # Constructed Answers
    if section_meta_id:
        derived_metadata_context.append(section_meta_id)

    # Metadata answers
    if canRender and section_meta_id:
        # Ensure a nested dict for this section inside the parent metadata dict
        if section_meta_id not in metadata_answers:
            metadata_answers[section_meta_id] = {}
        nested_metadata_answers = metadata_answers[section_meta_id]
    else:
        nested_metadata_answers = metadata_answers

    # Nested answers
    if canRender:
        if section_id not in nested_answers:
            nested_answers[section_id] = {}
        nested_nested_answers = nested_answers[section_id]
    else:
        nested_nested_answers = nested_answers

    # Possible answers
    if section_id not in possible_answers:
        possible_answers[section_id] = {}
    nested_possible_answers = possible_answers[section_id]

    fields = section.get("fields", [])
    if not isinstance(fields, list):
        print(f"⚠️ section.fields missing or not a list in section {section_id}")
        return

    for field in fields:
        if not isinstance(field, dict):
            print(f"⚠️ skipping invalid field in section {section_id}")
            continue

        dep_data = form_dep_data(form, field, derived_context, answers)
        if canRender and dep_data.get("canRender", True):
            # Pass nested_metadata_answers so the field can add its answers under this section's metadata
            walk_field(
                form,
                field,
                derived_context,
                derived_metadata_context,
                answers,
                answersWRTMetadata,
                True,
                nested_metadata_answers,
                nested_nested_answers,
                flat_answers,
                nested_possible_answers,
                constructed_answers,
            )
        else:
            # Pass nested_metadata_answers so the field can add its answers under this section's metadata
            walk_field(
                form,
                field,
                derived_context,
                derived_metadata_context,
                answers,
                answersWRTMetadata,
                False,
                nested_metadata_answers,
                nested_nested_answers,
                flat_answers,
                nested_possible_answers,
                constructed_answers,
            )
