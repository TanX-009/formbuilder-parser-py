from typing import List, Dict, Any

from .constant import form_context_split_str
from .answer import get_form_answer, are_form_answers_equal
from .defs import get_form_def


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
        context_from_path = resolve_context_path(form, dep["path"], context)
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
            can_render = can_render and this_visible

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

            aggregated_options.extend(chosen_options)
            can_render = can_render and len(chosen_options) > 0

        elif dep_type == "files":
            final_files: List[dict] = []
            if dep_answers and all(
                not isinstance(a, (str, int, bool)) for a in dep_answers
            ):
                final_files = dep_answers  # type: ignore

                # handle exclusions
                for exclude_path in dep.get("exclude", []):
                    exclude_context = resolve_context_path(form, exclude_path, context)
                    exclude_answers = get_form_answer(
                        exclude_context["wIdx"], form_answers
                    )
                    final_files = [
                        f for f in final_files if f["id"] not in exclude_answers
                    ]

            aggregated_files.extend(final_files)
            can_render = can_render and len(final_files) > 0

    return {
        "canRender": can_render,
        "options": aggregated_options,
        "files": aggregated_files,
    }
