from typing import Any, Dict


# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

VALID_FIELD_TYPES = {
    "text",
    "textarea",
    "password",
    "email",
    "number",
    "radio",
    "select",
    "checkbox",
    "multiselect",
    "fetchradio",
    "fetchselect",
    "fetchcheckbox",
    "fetchmultiselect",
    "mapper",
    "fileupload",
    "filesupload",
    "fileselect",
    "fileselectwrtlang",
    "subformwtable",
    "mirror",
}

SELECT_FIELD_TYPES = {
    "radio",
    "select",
    "checkbox",
    "multiselect",
    "fetchradio",
    "fetchselect",
    "fetchcheckbox",
    "fetchmultiselect",
}

BASIC_INPUT_FIELD_TYPES = {
    "text",
    "textarea",
    "password",
    "email",
    "number",
}


# ---------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------


def is_form_field(value: Any) -> bool:
    """
    Runtime equivalent of TS `value is TFormField`
    """
    if not isinstance(value, dict):
        return False

    field_type = value.get("type")
    return isinstance(field_type, str) and field_type in VALID_FIELD_TYPES


def is_select_field(value: Any) -> bool:
    """
    Strict select field validator (requires `options` array).
    Mirrors TS `isSelectField`.
    """
    if not isinstance(value, dict):
        return False

    field_type = value.get("type")
    options = value.get("options")

    return (
        isinstance(field_type, str)
        and field_type in SELECT_FIELD_TYPES
        and isinstance(options, list)
    )


def is_select_field_non_strict(value: Dict[str, Any]) -> bool:
    """
    Non-strict version (does NOT require `options`).
    Mirrors TS `isSelectFieldNonStrict`.
    """
    field_type = value.get("type")
    return isinstance(field_type, str) and field_type in SELECT_FIELD_TYPES


def is_basic_input_field(value: Any) -> bool:
    """
    Runtime equivalent of TS `value is TFormTextField | TFormNumberField`
    """
    if not isinstance(value, dict):
        return False

    field_type = value.get("type")
    return isinstance(field_type, str) and field_type in BASIC_INPUT_FIELD_TYPES
