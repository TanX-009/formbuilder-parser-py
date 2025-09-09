from typing import Dict, Any
from .constant import form_context_split_str
from .section import walk_section
from .dependency import form_dep_data


def walk_phase(
    form: dict,
    phase: dict,
    context: str,
    answers: dict,
    metadata_answers: Dict[str, Any],  # can be nested dict
) -> None:
    phase_id = phase.get("id", "<no-id>")
    derived_context = f"{context}{form_context_split_str}{phase_id}"

    # Phase-level metadata
    phase_meta_id = phase.get("metadata", {}).get("id")
    if phase_meta_id:
        # Ensure a nested dict for this phase
        if phase_meta_id not in metadata_answers:
            metadata_answers[phase_meta_id] = {}

        # This nested dict will be passed to sections
        nested_metadata = metadata_answers[phase_meta_id]
    else:
        # No metadata → just use the same top-level dict
        nested_metadata = metadata_answers

    sections = phase.get("sections", [])
    if not isinstance(sections, list):
        print(f"⚠️ sections missing or not a list in phase {phase_id}")
        return

    for section in sections:
        if not isinstance(section, dict):
            print(f"⚠️ skipping invalid section in phase {phase_id}")
            continue

        dep_data = form_dep_data(form, section, derived_context, answers)
        if not dep_data.get("canRender", True):
            print(f"🔒 Section {section.get('id', '<no-id>')} not renderable, skipping")
            continue

        # Pass the nested metadata dict to section
        walk_section(form, section, derived_context, answers, nested_metadata)
