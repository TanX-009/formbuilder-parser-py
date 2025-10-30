from typing import Any, Dict, List
from .constant import form_context_split_str
from .answer import get_form_answer, are_form_answers_equal
from .defs import get_form_def, is_section_triggered_one
from .util import fast_hash, has_answer, is_file_data_array


# --- Dependency Cache ---
_dep_cache: Dict[str, Dict[str, Any]] = {}


def reset_dep_cache():
    """Reset the dependency cache"""
    global _dep_cache
    _dep_cache = {}


def resolve_context_path(
    form: dict, dep_path: List[str], context: str
) -> Dict[str, str]:
    """
    Resolves a dependency path that may contain '*' wildcards into
    a full context string by replacing '*' with context parts.
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


def is_triggered_section_visible(
    parent_section: dict,
    triggered_section_id: str,
    answers: Dict[str, List[Any]],
    context: str,
) -> bool:
    """
    Checks if a section with triggered_section_id is visible by walking through
    parent_section’s fields and their triggers/options.
    """
    for field in parent_section.get("fields", []):
        field_path = [context, field["id"]]
        field_context = form_context_split_str.join(field_path)
        answer = get_form_answer(field_context, answers)

        # --- Field triggers ---
        for trig in field.get("triggers", []):
            if trig.get("id") == triggered_section_id and len(answer) > 0:
                return True

        # --- Option triggers ---
        if "options" not in field:
            continue

        for option in field["options"]:
            for trig in option.get("triggers", []):
                if trig.get("id") == triggered_section_id:
                    if has_answer(answer, option.get("value")):
                        return True
    return False


def form_dep_data(
    form: dict, node: dict, context: str, answers: Dict[str, List[Any]]
) -> Dict[str, Any]:
    """
    Resolves dependency data for a given form node (field or section).
    Handles visibility, options, and file dependencies with recursive parent evaluation.
    """
    if not node.get("dependency"):
        return {"canRender": True, "options": [], "files": []}
    if not answers:
        return {"canRender": False, "options": [], "files": []}

    can_render = True
    aggregated_options: List[dict] = []
    aggregated_files: List[dict] = []

    for dep in node.get("dependency", []):
        dep_hash = fast_hash(dep)

        # --- Check cache first ---
        # if dep_hash in _dep_cache:
        #     cached = _dep_cache[dep_hash]
        #     can_render = can_render and cached["canRender"]
        #     aggregated_options.extend(cached["options"])
        #     aggregated_files.extend(cached["files"])
        #     continue

        this_can_render = True
        this_options: List[dict] = []
        this_files: List[dict] = []

        context_from_path = resolve_context_path(form, dep["path"], context)

        # --- Recursive parent dependency evaluation ---
        for i in range(len(dep["path"]) - 2, -1, -1):
            parent_path = dep["path"][: i + 1]
            parent_context = resolve_context_path(form, parent_path, context)
            def_from_target = get_form_def(parent_context["woIdx"], form)

            if def_from_target:
                parent_dep_data = form_dep_data(
                    form, def_from_target, parent_context["wIdx"], answers
                )
                this_can_render = this_can_render and parent_dep_data["canRender"]

            # --- Handle triggered sections visibility ---
            triggered_section_parent = is_section_triggered_one(
                form, parent_context["woIdx"]
            )
            if not triggered_section_parent:
                continue

            parent_parent_path = parent_path[:-1]
            parent_parent_context = (
                form["id"]
                + form_context_split_str
                + form_context_split_str.join(parent_parent_path)
            )

            this_can_render = (
                this_can_render
                and not isinstance(triggered_section_parent, bool)
                and is_triggered_section_visible(
                    triggered_section_parent,
                    dep["path"][len(parent_path) - 1],
                    answers,
                    parent_parent_context,
                )
            )

        # --- Evaluate dependency type ---
        dep_answers = get_form_answer(context_from_path["wIdx"], answers)
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
            if dep_answers and is_file_data_array(dep_answers):
                final_files = dep_answers

                # handle exclusions
                for exclude_path in dep.get("exclude", []):
                    exclude_context = resolve_context_path(form, exclude_path, context)
                    exclude_answers = get_form_answer(exclude_context["wIdx"], answers)
                    final_files = [
                        f for f in final_files if f["id"] not in exclude_answers
                    ]
            this_files = final_files
            this_can_render = this_can_render and len(final_files) > 0

            this_files = final_files
            this_can_render = this_can_render and len(final_files) > 0

        # --- Aggregate and cache ---
        can_render = can_render and this_can_render
        aggregated_options.extend(this_options)
        aggregated_files.extend(this_files)

        _dep_cache[dep_hash] = {
            "canRender": this_can_render,
            "options": this_options,
            "files": this_files,
        }

    return {
        "canRender": can_render,
        "options": aggregated_options,
        "files": aggregated_files,
    }
