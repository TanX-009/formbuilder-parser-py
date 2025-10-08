from typing import List, Dict, Any

from form.utils import fast_hash

from .constant import form_context_split_str
from .answer import get_form_answer, are_form_answers_equal, has_answer
from .defs import get_form_def, is_section_triggered_one


def is_triggered_section_visible(
    parent_section: dict,
    triggered_section_id: str,
    answers: Dict[str, List[Any]],
    context: str,
) -> bool:
    """
    Checks if the section with `triggered_section_id` is visible based on any
    answer in the parent section's fields/options.
    """
    is_visible = False

    for field in parent_section.get("fields", []):
        field_context = form_context_split_str.join([context, field["id"]])
        answer = get_form_answer(field_context, answers)

        # Check field triggers
        for trig in field.get("triggers", []):
            if trig.get("id") == triggered_section_id and len(answer) > 0:
                is_visible = True
                break  # Exit the field loop early
        if is_visible:
            break

        # Check option triggers
        if "options" in field:
            for option in field["options"]:
                for trig in option.get("triggers", []):
                    if trig.get("id") == triggered_section_id:
                        # If any answer matches the option value, section is visible
                        if has_answer(answer, option.get("value")):
                            is_visible = True
                            break
                if is_visible:
                    break
        if is_visible:
            break

    return is_visible


def resolve_context_path(
    form: dict, dep_path: List[str], context: str
) -> Dict[str, str]:
    """
    Resolves a dependency path that may contain '*' wildcards
    into a full context string.
    """
    context_parts = context.split(form_context_split_str)
    resolved_path = [
        (context_parts[i + 1] if p == "*" and (i + 1) < len(context_parts) else p)
        for i, p in enumerate(dep_path)
    ]
    return {
        "wIdx": form["id"]
        + form_context_split_str
        + form_context_split_str.join(resolved_path),
        "woIdx": form["id"]
        + form_context_split_str
        + form_context_split_str.join(dep_path),
    }


# Simple in-memory cache (like depCache)
dep_cache: Dict[str, Dict[str, Any]] = {}


def form_dep_data(
    form: dict, node: dict, context: str, form_answers: Dict[str, List[Any]]
) -> Dict[str, Any]:
    """
    Resolves dependency data for a given form node (field or section)
    """
    if not node.get("dependency"):
        return {"canRender": True, "options": [], "files": []}

    if not form_answers:
        return {"canRender": False, "options": [], "files": []}

    can_render = True
    aggregated_options: List[dict] = []
    aggregated_files: List[dict] = []

    for dep in node.get("dependency", []):
        dep_hash = fast_hash(dep)
        if dep_hash in dep_cache:
            cached = dep_cache[dep_hash]
            can_render = can_render and cached["canRender"]
            aggregated_options.extend(cached["options"])
            aggregated_files.extend(cached["files"])
            continue

        this_can_render = True
        this_options: List[dict] = []
        this_files: List[dict] = []

        context_from_path = resolve_context_path(form, dep["path"], context)

        # Iterate parent paths in reverse (like TS)
        for i in range(len(dep["path"]) - 2, -1, -1):
            parent_path = dep["path"][: i + 1]
            parent_context = resolve_context_path(form, parent_path, context)
            def_from_target = get_form_def(parent_context["woIdx"], form)

            if def_from_target:
                parent_dep_data = form_dep_data(
                    form, def_from_target, parent_context["wIdx"], form_answers
                )
                this_can_render = this_can_render and parent_dep_data["canRender"]

            # Triggered sections
            triggered_section = is_section_triggered_one(form, parent_context["woIdx"])
            if not triggered_section or not isinstance(triggered_section, dict):
                continue

            parent_parent_path = parent_path[:-1]
            parent_parent_context = form_context_split_str.join(
                [form["id"], *parent_parent_path]
            )
            this_can_render = this_can_render and is_triggered_section_visible(
                triggered_section,
                dep["path"][len(parent_path) - 1],
                form_answers,
                parent_parent_context,
            )

        dep_answers = get_form_answer(context_from_path["wIdx"], form_answers)
        dep_type = dep.get("type")

        if dep_type == "visibility":
            this_visible = False
            if not dep.get("answers") and dep_answers:
                this_visible = True
            elif dep.get("answers"):
                for answer in dep["answers"]:
                    if are_form_answers_equal(answer, dep_answers):
                        this_visible = True
                        break
            this_can_render = this_can_render and this_visible

        elif dep_type == "options":
            chosen_options: List[dict] = []
            if dep_answers:
                def_from_target = get_form_def(context_from_path["woIdx"], form)
                if def_from_target and def_from_target.get("type") in [
                    "checkbox",
                    "radio",
                    "dropdown-multi-select",
                    "dropdown-single-select",
                ]:
                    options_from_target = def_from_target.get("options", [])
                    chosen_options = [
                        opt
                        for opt in options_from_target
                        if opt["value"] in dep_answers
                    ]
            this_options = chosen_options
            this_can_render = this_can_render and len(chosen_options) > 0

        elif dep_type == "files":
            final_files: List[dict] = []
            if dep_answers and all(
                not isinstance(a, (str, int, bool)) for a in dep_answers
            ):
                final_files = dep_answers  # type: ignore
                for exclude_path in dep.get("exclude", []):
                    exclude_context = resolve_context_path(form, exclude_path, context)
                    exclude_answers = get_form_answer(
                        exclude_context["wIdx"], form_answers
                    )
                    final_files = [
                        f for f in final_files if f["id"] not in exclude_answers
                    ]
            this_files = final_files
            this_can_render = this_can_render and len(final_files) > 0

        # --- aggregate ---
        can_render = can_render and this_can_render
        aggregated_options.extend(this_options)
        aggregated_files.extend(this_files)

        # --- cache ---
        dep_cache[dep_hash] = {
            "canRender": this_can_render,
            "options": this_options,
            "files": this_files,
        }

    return {
        "canRender": can_render,
        "options": aggregated_options,
        "files": aggregated_files,
    }
