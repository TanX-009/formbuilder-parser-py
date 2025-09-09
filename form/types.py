from typing import List, Literal, Optional, TypedDict


class TFormAnswerFileData(TypedDict):
    """Represents uploaded file metadata stored in a form answer."""

    id: str  # Unique ID for the file entry
    file: str  # Placeholder: File objects aren’t directly portable in JSON, use a path or encoded string
    name: str  # Original file name
    size: int  # File size in bytes
    type: str  # Always 'application/pdf'
    language: str  # Language code associated with the file
    url: str  # Object URL for local preview


class TFormAnswerPair(TypedDict):
    """Left-hand/right-hand pair answer."""

    lhs: Union[str, int]
    rhs: Union[str, int]


# Possible answer types in a form field
TFormAnswer = Union[str, int, bool, TFormAnswerPair, TFormAnswerFileData]


class TForm(TypedDict):
    """Form definition with metadata and phases."""

    id: str
    title: str
    type: Literal["form"]
    metadata: Optional[TFormMetadata]
    phases: List[TFormPhase]
    reviewPhaseLabel: Optional[str]


class TFormPhase(TypedDict):
    """Definition of a form phase."""

    id: str
    label: str
    title: str
    description: Optional[str]
    type: Literal["phase"]
    subtype: Literal["main", "sub"]
    dependency: Optional[List[TFormDependency]]
    sections: List[TFormSection]
    metadata: Optional[TFormMetadata]


# --- Field Option ---
class TFormFieldOption(TypedDict, total=False):
    id: str
    label: str
    value: str
    decoration: Optional[dict]  # {"type": "tag", "fg": str, "bg": str}
    note: Optional[str]
    triggers: Optional[List[TFormSection]]
    metadata: Optional[TFormMetadata]


# --- Base Field ---
class TFormBaseField(TypedDict, total=False):
    id: str
    required: bool
    label: str
    dependency: Optional[List[TFormDependency]]
    placeholder: Optional[str]
    hint: Optional[str]
    note: Optional[str]
    triggers: Optional[List[TFormSection]]
    metadata: Optional[TFormMetadata]


# --- Specific Field Types ---
class TFormTextField(TFormBaseField, total=False):
    type: Literal["text", "textarea", "number", "password"]
    default: Optional[str]
    addable: Optional[dict]  # {"label": str}


class TFormSingleSelectField(TFormBaseField, total=False):
    type: Literal["radio", "dropdown-single-select"]
    options: List[TFormFieldOption]
    default: Optional[str]  # references TFormFieldOption["value"]


class TFormMultiSelectField(TFormBaseField, total=False):
    type: Literal["checkbox", "dropdown-multi-select"]
    options: List[TFormFieldOption]
    default: Optional[List[str]]


class TFormMapperField(TFormBaseField, total=False):
    type: Literal["mapper"]
    rhsOptions: List[TFormFieldOption]
    lhsLabel: str
    rhsLabel: str


class TFormFileUploadField(TFormBaseField, total=False):
    type: Literal["fileupload"]
    filetype: str  # from TFormAnswerFileData["type"]


class TFormFilesUploadField(TFormBaseField, total=False):
    type: Literal["filesupload"]
    filetypes: List[str]  # from TFormAnswerFileData["type"][]
    langOptions: List[TFormFieldOption]
    minimum: Optional[int]


class TFormFileSelectField(TFormBaseField, total=False):
    type: Literal["fileselect"]
    # NOTE: runtime validation for below is required
    # at least one with type='files'


class TFormSubFormwTableField(TFormBaseField, total=False):
    type: Literal["subformwtable"]
    phases: List[dict]  # reference to TFormPhase (to be expanded later)
    # tableColConf: List[TFormSubFormTableCol]


class TFormMirrorField(TFormBaseField, total=False):
    type: Literal["mirror"]
    path: List[str]


# --- Union Type ---
TFormField = (
    TFormTextField
    | TFormSingleSelectField
    | TFormMultiSelectField
    | TFormMapperField
    | TFormFileUploadField
    | TFormFilesUploadField
    | TFormFileSelectField
    | TFormSubFormwTableField
    | TFormMirrorField
)


class TFormSection(TypedDict):
    """Definition of a form section."""

    id: str
    title: str
    type: Literal["section"]
    description: Optional[str]
    fields: List[TFormField]
    dependency: Optional[List[TFormDependency]]
    layout: Optional[List[List[str]]]
    metadata: Optional[TFormMetadata]


# --- Dependency Types ---
class TFieldDependency(TypedDict):
    """Base dependency: points to another field."""

    path: List[str]


class TFieldAnswer(TFieldDependency, total=False):
    type: Literal["visibility"]
    answers: Optional[List[List[TFormAnswer]]]


class TFieldOptions(TFieldDependency, total=False):
    type: Literal["options"]
    exclude: Optional[List[str]]


class TFieldSelectedFiles(TFieldDependency, total=False):
    type: Literal["files"]
    exclude: Optional[List[List[str]]]


# --- Aggregated Dependency ---
TFormDependency = TFieldAnswer | TFieldOptions | TFieldSelectedFiles


# --- Dependency Data after evaluation ---
class TFormDepData(TypedDict):
    canRender: bool
    options: List[TFormFieldOption]
    files: List[TFormAnswerFileData]


TFormTrigger = TFormSection
