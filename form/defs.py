from typing import List, Dict, Optional, Any, Union
from .constant import form_context_split_str

# --- Global caches ---
form_field_defs_cache: Dict[str, dict] = {}
required_field_cache: Dict[str, List[str]] = {}
is_section_triggered_one_cache: Dict[str, str | bool] = {}


def is_section_triggered_one(
    form: dict, context: str, form_context_split_str: str = "__"
) -> dict | bool:
    """
    Checks if the section at 'context' was triggered from any parent section's field.
    """
    cached = is_section_triggered_one_cache.get(context)
    if context in is_section_triggered_one_cache:
        if not cached or not isinstance(cached, str):
            return False
        parent_def = get_form_def(cached, form)
        if parent_def and parent_def.get("type") == "section":
            return parent_def
        return False

    path = context.split(form_context_split_str)
    parent_path = path[:-1]
    parent_context = form_context_split_str.join(parent_path)

    parent_def = get_form_def(parent_context, form)
    if not parent_def:
        is_section_triggered_one_cache[context] = False
        return False

    if parent_def.get("type") != "section":
        is_section_triggered_one_cache[context] = False
        return False

    for field in parent_def.get("fields", []):
        # field triggers
        for trigger in field.get("triggers", []):
            if trigger.get("id") == path[-1]:
                is_section_triggered_one_cache[context] = parent_context
                return parent_def

        # option triggers
        if "options" in field:
            for option in field["options"]:
                for trigger in option.get("triggers", []):
                    if trigger.get("id") == path[-1]:
                        is_section_triggered_one_cache[context] = parent_context
                        return parent_def

    is_section_triggered_one_cache[context] = False
    return False

# Cache for isSectionTriggeredOne
is_section_triggered_one_cache: Dict[str, Union[bool, str]] = {}


def is_section_triggered_one(form: dict, context: str) -> Union[bool, Optional[dict]]:
    """
    Checks if the section at `context` was triggered from any parent section's field.
    Returns False if not triggered, or the parent section dict if triggered.
    """
    if context in is_section_triggered_one_cache:
        cached = is_section_triggered_one_cache[context]
        if not cached:  # cached is False
            return False
        # cached is guaranteed to be str here
        parent_def = get_form_def(str(cached), form)
        if parent_def and parent_def.get("type") == "section":
            return parent_def
        return False

    path_parts = context.split(form_context_split_str)
    parent_path_parts = path_parts[:-1]
    parent_context = form_context_split_str.join(parent_path_parts)

    parent_def = get_form_def(parent_context, form)
    if not parent_def or parent_def.get("type") != "section":
        is_section_triggered_one_cache[context] = False
        return False

    target_section_id = path_parts[-1]

    for field in parent_def.get("fields", []):
        # Check field triggers
        for trig in field.get("triggers", []):
            if trig.get("id") == target_section_id:
                is_section_triggered_one_cache[context] = parent_context
                return parent_def

        # Check option triggers
        for option in field.get("options", []):
            for trig in option.get("triggers", []):
                if trig.get("id") == target_section_id:
                    is_section_triggered_one_cache[context] = parent_context
                    return parent_def

    is_section_triggered_one_cache[context] = False
    return False


def get_form_def(context: str, form: dict) -> Optional[dict]:
    """
    Retrieves the node (phase/section/field) at the given context.
    Supports:
    - Phase → Section → Field hierarchy
    - Subform fields (with "*" marker)
    - Triggered sections (recursively nested)
    - Caching for phases, sections, and fields
    """
    if context in form_field_defs_cache:
        return form_field_defs_cache[context]

    split = context.split(form_context_split_str)
    current_form = form
    current_phase = None
    current_section = None
    current_field = None

    for idx in range(1, len(split)):
        key = split[idx]

        # --- Phase level ---
        if current_form:
            phase = next(
                (p for p in current_form.get("phases", []) if p["id"] == key), None
            )
            if not phase:
                return None

            current_form = None
            current_phase = phase
            current_section = None
            current_field = None

            # cache & return if last
            if idx == len(split) - 1 and key == current_phase["id"]:
                form_field_defs_cache[context] = current_phase
                return current_phase
            continue

        # --- Section level ---
        if current_phase:
            section = next(
                (s for s in current_phase.get("sections", []) if s["id"] == key), None
            )
            if not section:
                return None

            current_form = None
            current_phase = None
            current_section = section
            current_field = None

            # cache & return if last
            if idx == len(split) - 1 and key == current_section["id"]:
                form_field_defs_cache[context] = current_section
                return current_section
            continue

        # --- Field / Trigger level ---
        if current_section:
            # 1) Direct field match
            field = next(
                (f for f in current_section.get("fields", []) if f["id"] == key), None
            )
            if field:
                current_form = None
                current_phase = None
                current_section = None
                current_field = field

                # cache & return if last
                if idx == len(split) - 1:
                    form_field_defs_cache[context] = current_field
                    return current_field
                continue

            # 2) Triggered section match
            matched_trigger = None
            for field_i in current_section.get("fields", []):
                # inside options
                for opt in field_i.get("options", []):
                    for trig in opt.get("triggers", []):
                        if trig.get("id") == key:
                            matched_trigger = trig
                            break
                    if matched_trigger:
                        break

                # direct field triggers
                for trig in field_i.get("triggers", []):
                    if trig.get("id") == key:
                        matched_trigger = trig
                        break

                if matched_trigger:
                    break

            if matched_trigger:
                current_form = None
                current_phase = None
                current_section = matched_trigger
                current_field = None

                # cache & return if last
                if idx == len(split) - 1 and key == matched_trigger["id"]:
                    form_field_defs_cache[context] = current_section
                    return current_section
                continue

            return None

        # --- Subform handling ---
        if current_field:
            if idx == len(split) - 1:
                form_field_defs_cache[context] = current_field
                return current_field

            if current_field.get("type") == "subformwtable":
                star_marker = split[idx]
                if star_marker != "*":
                    return None
                current_form = {"phases": current_field.get("phases", [])}
                current_phase = None
                current_section = None
                current_field = None
                continue

    return None


def reset_required_field_cache():
    global required_field_cache
    required_field_cache = {}


def reset_required_field_cache_for_form(base_context: str):
    global required_field_cache
    keys_to_delete = [k for k in required_field_cache if k.startswith(base_context)]
    for k in keys_to_delete:
        del required_field_cache[k]


def collect_visible_required_fields_from_phases(
    form: dict, phases: List[dict], base_context: str, answers: Dict[str, List[Any]]
) -> List[str]:
    """
    Collects all required fields from an array of phases.
    Caches per-node (phase/section/trigger section) to avoid re-walking.
    """
    from .dependency import form_dep_data

    required_contexts: List[str] = []

    def walk_section(section: dict, path_parts: List[str]) -> List[str]:
        section_context = form_context_split_str.join(path_parts)
        if section_context in required_field_cache:
            return required_field_cache[section_context]

        local_required: List[str] = []

        for field in section.get("fields", []):
            path_parts.append(field["id"])
            field_context = form_context_split_str.join(path_parts)

            dep_data = form_dep_data(form, field, field_context, answers)
            if dep_data.get("canRender"):
                if field.get("required"):
                    local_required.append(field_context)

                # recurse into triggers
                for trig in field.get("triggers", []):
                    if trig.get("type") == "section":
                        path_parts.append(trig["id"])
                        local_required.extend(walk_section(trig, path_parts))
                        path_parts.pop()

            path_parts.pop()

        required_field_cache[section_context] = local_required
        return local_required

    def walk_phase(phase: dict, path_parts: List[str]) -> List[str]:
        path_parts.append(phase["id"])
        phase_context = form_context_split_str.join(path_parts)

        if phase_context in required_field_cache:
            path_parts.pop()
            return required_field_cache[phase_context]

        local_required: List[str] = []
        dep_data = form_dep_data(form, phase, phase_context, answers)
        if dep_data.get("canRender"):
            for section in phase.get("sections", []):
                path_parts.append(section["id"])
                sec_dep_data = form_dep_data(
                    form, section, form_context_split_str.join(path_parts), answers
                )
                if sec_dep_data.get("canRender"):
                    local_required.extend(walk_section(section, path_parts))
                path_parts.pop()

        required_field_cache[phase_context] = local_required
        path_parts.pop()
        return local_required

    base_parts = [base_context]
    for phase in phases:
        required_contexts.extend(walk_phase(phase, base_parts))

    return required_contexts
