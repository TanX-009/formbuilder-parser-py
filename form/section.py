from typing import Dict, Any, Optional
from .constant import form_context_split_str
from .field import walk_field
from .dependency import form_dep_data


async def walk_section(
    form: dict,
    section: dict,
    context: str,
    metadata_context: list[str],
    answers: dict,
    answersWRTMetadata: Optional[dict],
    canRender: bool,
    metadata_answers: Dict[str, Any],
    nested_answers: Dict[str, Any],
    flat_answers: Dict[str, Any],
    possible_answers: Dict[str, Any],
    constructed_answers: Dict[str, Any],
) -> None:
    """
    Walk over fields in a section and call walk_field for each field.

    ⚠️ IMPORTANT:
    - Preserves old extraction semantics
    - Async options are resolved ONLY to enrich possible_answers
    - Rendering logic is NOT replicated
    """

    section_id = section.get("id", "<no-id>")
    derived_context = f"{context}{form_context_split_str}{section_id}"

    derived_metadata_context = list(metadata_context)

    section_meta_id = section.get("metadata", {}).get("id")

    # ------------------------------------------------------------------
    # Metadata answers nesting (unchanged)
    # ------------------------------------------------------------------
    if section_meta_id:
        derived_metadata_context.append(section_meta_id)

    if canRender and section_meta_id:
        metadata_answers.setdefault(section_meta_id, {})
        nested_metadata_answers = metadata_answers[section_meta_id]
    else:
        nested_metadata_answers = metadata_answers

    # ------------------------------------------------------------------
    # Nested answers (unchanged)
    # ------------------------------------------------------------------
    if canRender:
        nested_answers.setdefault(section_id, {})
        nested_nested_answers = nested_answers[section_id]
    else:
        nested_nested_answers = nested_answers

    # ------------------------------------------------------------------
    # Possible answers (unchanged)
    # ------------------------------------------------------------------
    possible_answers.setdefault(section_id, {})
    nested_possible_answers = possible_answers[section_id]

    fields = section.get("fields", [])
    if not isinstance(fields, list):
        print(f"⚠️ section.fields missing or not a list in section {section_id}")
        return

    # ------------------------------------------------------------------
    # Field traversal
    # ------------------------------------------------------------------
    for field in fields:
        if not isinstance(field, dict):
            print(f"⚠️ skipping invalid field in section {section_id}")
            continue

        dep_data = form_dep_data(form, field, derived_context, answers)

        field_can_render = canRender and dep_data.get("canRender", True)

        # --------------------------------------------------------------
        # ASYNC OPTIONS HANDLING (NEW, SAFE)
        # --------------------------------------------------------------
        if field_can_render and callable(dep_data.get("options")):
            try:
                options = await dep_data["options"]()
                # Attach resolved options ONLY for extraction
                dep_data = {**dep_data, "options": options}
            except Exception as e:
                # Do NOT break traversal
                dep_data = {**dep_data, "options": []}
                print(f"⚠️ failed to fetch options for field {field.get('id')}: {e}")

        if not dep_data["options"] or not field_can_render:
            dep_data["options"] = []
        # --------------------------------------------------------------
        # Delegate to walk_field (UNCHANGED CONTRACT)
        # --------------------------------------------------------------
        await walk_field(
            form,
            field,
            derived_context,
            derived_metadata_context,
            answers,
            answersWRTMetadata,
            field_can_render,
            nested_metadata_answers,
            nested_nested_answers,
            flat_answers,
            nested_possible_answers,
            constructed_answers,
            dep_data,  # 🔑 NEW: pass dep_data explicitly
        )
