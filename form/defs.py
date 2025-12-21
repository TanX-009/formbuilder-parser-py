from typing import Dict, Literal, Optional, Union
from .constant import form_context_split_str
from .field_validator import is_form_field

# ---------------------------------------------------------------------
# Global caches
# ---------------------------------------------------------------------

# context -> node
form_field_defs_cache: Dict[str, dict] = {}

# context -> False | {"parent": parent_context, "field": field_context}
is_section_triggered_one_cache: Dict[str, Union[Literal[False], Dict[str, str]]] = {}


# ---------------------------------------------------------------------
# is_section_triggered_one
# ---------------------------------------------------------------------
def is_section_triggered_one(
    form: dict, context: str
) -> Union[Literal[False], Dict[str, dict]]:
    """
    Checks whether the section at `context` was triggered by a field
    in its parent section.

    Returns:
      False
      or { "parent": <parent_section_def>, "field": <field_def> }
    """

    # ---- Cache hit ----
    if context in is_section_triggered_one_cache:
        cached = is_section_triggered_one_cache[context]
        if not cached:
            return False

        parent_def = get_form_def(cached["parent"], form)
        field_def = get_form_def(cached["field"], form)

        if (
            parent_def
            and parent_def.get("type") == "section"
            and field_def
            and is_form_field(field_def)
        ):
            return {"parent": parent_def, "field": field_def}

        return False

    path = context.split(form_context_split_str)
    parent_path = path[:-1]
    parent_context = form_context_split_str.join(parent_path)
    target_section_id = path[-1]

    parent_def = get_form_def(parent_context, form)
    if not parent_def or parent_def.get("type") != "section":
        is_section_triggered_one_cache[context] = False
        return False

    for field in parent_def.get("fields", []):
        field_context = parent_context + form_context_split_str + field["id"]

        # --- Field triggers ---
        for trig in field.get("triggers", []):
            if trig.get("id") == target_section_id:
                is_section_triggered_one_cache[context] = {
                    "parent": parent_context,
                    "field": field_context,
                }
                return {"parent": parent_def, "field": field}

        # --- Option triggers ---
        if "options" in field:
            for opt in field.get("options", []):
                for trig in opt.get("triggers", []):
                    if trig.get("id") == target_section_id:
                        is_section_triggered_one_cache[context] = {
                            "parent": parent_context,
                            "field": field_context,
                        }
                        return {"parent": parent_def, "field": field}

    is_section_triggered_one_cache[context] = False
    return False


# ---------------------------------------------------------------------
# get_form_def
# ---------------------------------------------------------------------
def get_form_def(context: str, form: dict) -> Optional[dict]:
    """
    Resolves a form node (phase / section / field / triggered section)
    for a given context path.

    Supports:
    - Phase → Section → Field
    - Triggered sections
    - Subform fields using "*"
    - Caching
    """

    if context in form_field_defs_cache:
        return form_field_defs_cache[context]

    split = context.split(form_context_split_str)

    current_form: Optional[dict] = form
    current_phase: Optional[dict] = None
    current_section: Optional[dict] = None
    current_field: Optional[dict] = None

    for idx in range(1, len(split)):
        key = split[idx]

        # ---- Phase ----
        if current_form:
            phase = next(
                (p for p in current_form.get("phases", []) if p["id"] == key),
                None,
            )
            if not phase:
                return None

            current_form = None
            current_phase = phase
            current_section = None
            current_field = None

            if idx == len(split) - 1:
                form_field_defs_cache[context] = phase
                return phase
            continue

        # ---- Section ----
        if current_phase:
            section = next(
                (s for s in current_phase.get("sections", []) if s["id"] == key),
                None,
            )
            if not section:
                return None

            current_phase = None
            current_section = section
            current_field = None

            if idx == len(split) - 1:
                form_field_defs_cache[context] = section
                return section
            continue

        # ---- Field / Triggered Section ----
        if current_section:
            # 1) Direct field
            field = next(
                (f for f in current_section.get("fields", []) if f["id"] == key),
                None,
            )
            if field:
                current_section = None
                current_field = field

                if idx == len(split) - 1:
                    form_field_defs_cache[context] = field
                    return field
                continue

            # 2) Triggered section
            matched_trigger = None
            for field_i in current_section.get("fields", []):
                # option triggers
                for opt in field_i.get("options", []):
                    for trig in opt.get("triggers", []):
                        if trig.get("id") == key:
                            matched_trigger = trig
                            break
                    if matched_trigger:
                        break

                # field triggers
                for trig in field_i.get("triggers", []):
                    if trig.get("id") == key:
                        matched_trigger = trig
                        break

                if matched_trigger:
                    break

            if matched_trigger:
                current_section = matched_trigger
                current_field = None

                if idx == len(split) - 1:
                    form_field_defs_cache[context] = matched_trigger
                    return matched_trigger
                continue

            return None

        # ---- Subform ----
        if current_field:
            if idx == len(split) - 1:
                form_field_defs_cache[context] = current_field
                return current_field

            if current_field.get("type") == "subformwtable":
                if split[idx] != "*":
                    return None

                current_form = {"phases": current_field.get("phases", [])}
                current_phase = None
                current_section = None
                current_field = None
                continue

    return None
