from typing import List, Dict, Optional, Any
from .constant import form_context_split_str

# Global caches
form_field_defs_cache: Dict[str, dict] = {}
required_field_cache: Dict[str, List[str]] = {}


def get_form_def(context: str, form: dict) -> Optional[dict]:
    """
    Retrieves the node (phase/section/field) at the given context.
    Supports subform "*" and triggered sections.
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

        if current_form:
            phase = next(
                (p for p in current_form.get("phases", []) if p["id"] == key), None
            )
            if not phase:
                return None
            current_form = None
            current_phase = phase

            # return phase if last segment matches
            if idx == len(split) - 1 and key == current_phase["id"]:
                return current_phase
            continue

        if current_phase:
            section = next(
                (s for s in current_phase.get("sections", []) if s["id"] == key), None
            )
            if not section:
                return None
            current_phase = None
            current_section = section

            # return section if last segment matches
            if idx == len(split) - 1 and key == current_section["id"]:
                return current_section
            continue

        if current_section:
            # 1) direct field match
            field = next(
                (f for f in current_section.get("fields", []) if f["id"] == key), None
            )
            if field:
                current_field = field
                if idx == len(split) - 1:
                    form_field_defs_cache[context] = current_field
                    return current_field
                continue

            # 2) triggered sections inside fields
            matched_trigger = None
            for field_i in current_section.get("fields", []):
                # triggers inside options
                for opt in field_i.get("options", []):
                    for trig in opt.get("triggers", []):
                        if trig["id"] == key:
                            matched_trigger = trig
                            break
                    if matched_trigger:
                        break

                # triggers on field itself
                for trig in field_i.get("triggers", []):
                    if trig["id"] == key:
                        matched_trigger = trig
                        break

                if matched_trigger:
                    break

            if matched_trigger:
                current_section = matched_trigger
                current_field = None
                continue

            return None

        if current_field:
            if idx == len(split) - 1:
                form_field_defs_cache[context] = current_field
                return current_field

            if current_field.get("type") == "subformwtable" and split[idx] == "*":
                current_form = {"phases": current_field.get("phases", [])}
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
    Collect all required fields from phases, taking dependency visibility into account.
    Uses caching to avoid repeated traversal.
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
            if dep_data["canRender"]:
                if field.get("required"):
                    local_required.append(field_context)

                # traverse triggers
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
        if dep_data["canRender"]:
            for section in phase.get("sections", []):
                path_parts.append(section["id"])
                sec_dep_data = form_dep_data(
                    form, section, form_context_split_str.join(path_parts), answers
                )
                if sec_dep_data["canRender"]:
                    local_required.extend(walk_section(section, path_parts))
                path_parts.pop()

        required_field_cache[phase_context] = local_required
        path_parts.pop()
        return local_required

    base_parts = [base_context]
    for phase in phases:
        required_contexts.extend(walk_phase(phase, base_parts))

    return required_contexts
