from typing import Optional, TypedDict


class TFormMetadata(TypedDict, total=False):
    """Metadata about the form."""

    id: Optional[str]
    title: Optional[str]
    description: Optional[str]
    hint: Optional[str]
    note: Optional[str]
    createdAt: Optional[str]  # ISO 8601 timestamp
