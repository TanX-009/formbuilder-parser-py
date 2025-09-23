from typing import Dict, Any, Optional
from .constant import form_context_split_str
from .section import walk_section
from .dependency import form_dep_data


def walk_phase(
    form: dict,
    phase: dict,
    context: str,
    metadata_context: list[str],
    answers: dict,
    answersWRTMetadata: Optional[dict],
    canRender: bool,
    metadata_answers: Dict[str, Any],  # can be nested dict
    nested_answers: Dict[str, Any],
    flat_answers: Dict[str, Any],
    possible_answers: Dict[str, Any],
    constructed_answers: Dict[str, Any],
) -> None:
    phase_id = phase.get("id", "<no-id>")
    derived_context = f"{context}{form_context_split_str}{phase_id}"
    derived_metadata_context = []
    derived_metadata_context.extend(metadata_context)

    sections = phase.get("sections", [])
    if not isinstance(sections, list):
        print(f"⚠️ sections missing or not a list in phase {phase_id}")
        return

    # Metadata Answers
    phase_meta_id = phase.get("metadata", {}).get("id")

    # Constructed Answers
    if phase_meta_id:
        derived_metadata_context.append(phase_meta_id)

    if canRender and phase_meta_id:
        # Ensure a nested dict for this phase
        if phase_meta_id not in metadata_answers:
            metadata_answers[phase_meta_id] = {}

        # This nested dict will be passed to sections
        nested_metadata_answers = metadata_answers[phase_meta_id]
    else:
        # No metadata → just use the same top-level dict
        nested_metadata_answers = metadata_answers

    # Nested answers
    if canRender:
        if phase_id not in nested_answers:
            nested_answers[phase_id] = {}
        nested_nested_answers = nested_answers[phase_id]
    else:
        nested_nested_answers = nested_answers

    # Possible answers
    if phase_id not in possible_answers:
        possible_answers[phase_id] = {}
    nested_possible_answers = possible_answers[phase_id]

    for section in sections:
        if not isinstance(section, dict):
            print(f"⚠️ skipping invalid section in phase {phase_id}")
            continue

        dep_data = form_dep_data(form, section, derived_context, answers)
        # if the phase can render and the section can render then handle the premium answers
        if canRender and dep_data.get("canRender", True):
            # Pass the nested metadata dict to section
            walk_section(
                form,
                section,
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
        # else walk for non-premium answers
        else:
            walk_section(
                form,
                section,
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
