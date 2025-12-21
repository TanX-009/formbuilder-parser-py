from typing import Any, Dict, List, Callable
from .constant import form_context_split_str
from .answer import (
    get_form_answer,
    are_form_answers_equal,
    has_answer,
)
from .defs import get_form_def, is_section_triggered_one
from .util import is_file_data_array, dedupe_form_field_options
from .options import get_form_options


# ---------------------------------------------------------------------
# Dependency Cache (disabled like TS)
# ---------------------------------------------------------------------
_dep_cache: Dict[str, Dict[str, Any]] = {}


def reset_dep_cache():
    global _dep_cache
    _dep_cache = {}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def resolve_context_path(
    form: dict, dep_path: List[str], context: str
) -> Dict[str, str]:
    context_parts = context.split(form_context_split_str)

    resolved = [
        context_parts[i + 1] if p == "*" and i + 1 < len(context_parts) else p
        for i, p in enumerate(dep_path)
    ]

    return {
        "wIdx": form["id"]
        + form_context_split_str
        + form_context_split_str.join(resolved),
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
    for field in parent_section.get("fields", []):
        field_context = context + form_context_split_str + field["id"]
        answer = get_form_answer(field_context, answers)

        # field triggers
        for trig in field.get("triggers", []):
            if trig["id"] == triggered_section_id and answer:
                return True

        if "options" not in field:
            continue

        # option triggers
        for opt in field["options"]:
            for trig in opt.get("triggers", []):
                if trig["id"] == triggered_section_id:
                    if has_answer(answer, opt.get("value")):
                        return True

    return False


# ---------------------------------------------------------------------
# Parent visibility (CRITICAL)
# ---------------------------------------------------------------------
def check_parent_visibility(
    form: dict,
    answers: Dict[str, List[Any]],
    context: str,
    dep: dict,
) -> bool:
    can_render = True

    for i in range(len(dep["path"]) - 2, -1, -1):
        if not can_render:
            break

        parent_path = dep["path"][: i + 1]
        parent_ctx = resolve_context_path(form, parent_path, context)

        parent_def = get_form_def(parent_ctx["woIdx"], form)
        if parent_def:
            parent_dep_data = form_dep_data(
                form, parent_def, parent_ctx["wIdx"], answers
            )
            can_render = can_render and parent_dep_data["canRender"]

        triggered = is_section_triggered_one(form, parent_ctx["woIdx"])
        if not triggered or not isinstance(triggered, dict):
            continue

        parent_parent_path = parent_path[:-1]
        parent_parent_ctx = (
            form["id"]
            + form_context_split_str
            + form_context_split_str.join(parent_parent_path)
        )

        can_render = can_render and is_triggered_section_visible(
            triggered["parent"],
            dep["path"][len(parent_path) - 1],
            answers,
            parent_parent_ctx,
        )

    return can_render


# ---------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------
def check_visibility_dep(dep_answers: List[Any], dep: dict) -> bool:
    if not dep.get("answers") and dep_answers:
        return True

    for ans in dep.get("answers", []):
        if are_form_answers_equal(ans, dep_answers):
            return True

    return False


async def get_chosen_options_of_dep(
    form: dict,
    context: str,
    answers: Dict[str, List[Any]],
    dep: dict,
    dep_answers: List[Any],
    context_from_path: Dict[str, str],
) -> List[dict]:
    chosen: List[dict] = []

    if not dep_answers:
        return chosen

    defn = get_form_def(context_from_path["woIdx"], form)
    if not defn:
        return chosen

    # static options
    if defn.get("type") in {
        "checkbox",
        "radio",
        "multiselect",
        "select",
    }:
        chosen = [opt for opt in defn.get("options", []) if opt["value"] in dep_answers]

    # fetched options
    elif defn.get("type") in {
        "fetchcheckbox",
        "fetchradio",
        "fetchmultiselect",
        "fetchselect",
    }:
        fetched = await get_form_options(defn["url"], defn["mapping"])
        merged = dedupe_form_field_options([defn.get("options", []), fetched])
        chosen = [o for o in merged if o["value"] in dep_answers]

    # exclusions
    for ex in dep.get("exclude", []):
        ex_ctx = resolve_context_path(form, ex, context)
        exclude_vals = get_form_answer(ex_ctx["wIdx"], answers)
        chosen = [o for o in chosen if o["id"] not in exclude_vals]

    return chosen


def get_files_of_dep(
    form: dict,
    context: str,
    answers: Dict[str, List[Any]],
    dep_answers: List[Any],
    dep: dict,
) -> List[dict]:
    if not dep_answers or not is_file_data_array(dep_answers):
        return []

    files = list(dep_answers)

    for ex in dep.get("exclude", []):
        ex_ctx = resolve_context_path(form, ex, context)
        exclude_vals = get_form_answer(ex_ctx["wIdx"], answers)
        files = [f for f in files if f["id"] not in exclude_vals]

    return files


# ---------------------------------------------------------------------
# Generate dep data (single dependency)
# ---------------------------------------------------------------------
def generate_dep_data(
    form: dict,
    answers: Dict[str, List[Any]],
    context: str,
    dep: dict,
):
    can_render = True
    options_promises: List[Callable] = []
    files: List[dict] = []

    ctx = resolve_context_path(form, dep["path"], context)

    can_render = can_render and check_parent_visibility(form, answers, context, dep)

    dep_answers = get_form_answer(ctx["wIdx"], answers)

    if dep["type"] == "visibility":
        can_render = can_render and check_visibility_dep(dep_answers, dep)

    elif dep["type"] == "options":
        options_promises.append(
            lambda: get_chosen_options_of_dep(
                form, context, answers, dep, dep_answers, ctx
            )
        )

    elif dep["type"] == "files":
        files = get_files_of_dep(form, context, answers, dep_answers, dep)
        can_render = can_render and bool(files)

    return {
        "canRender": can_render,
        "options": options_promises,
        "files": files,
    }


# ---------------------------------------------------------------------
# Public API (matches TS formDepData)
# ---------------------------------------------------------------------
def form_dep_data(
    form: dict,
    node: dict,
    context: str,
    answers: Dict[str, List[Any]],
) -> Dict[str, Any]:
    if not node.get("dependency"):
        return {"canRender": True, "options": None, "files": []}

    if not answers:
        return {"canRender": False, "options": None, "files": []}

    can_render = True
    option_promises: List[Callable] = []
    files: List[dict] = []

    for dep in node["dependency"]:
        dep_data = generate_dep_data(form, answers, context, dep)

        can_render = can_render and dep_data["canRender"]
        option_promises.extend(dep_data["options"])
        files.extend(dep_data["files"])

    async def options_resolver():
        results = []
        for fn in option_promises:
            results.append(await fn())
        return dedupe_form_field_options(results)

    return {
        "canRender": can_render,
        "options": options_resolver if option_promises else None,
        "files": files,
    }
