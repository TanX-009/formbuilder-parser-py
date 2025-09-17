import sys
import json
from pathlib import Path

from form.form import walk_form


def load_json(file_path: str):
    """Load and return JSON from a file path."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <form_definition.json> <answers.json>")
        sys.exit(1)

    form_file = sys.argv[1]
    ans_file = sys.argv[2]

    form_json = load_json(form_file)
    ans_json = load_json(ans_file)

    metadata, nested, flat = walk_form(form_json, ans_json)

    print("\n============ Metadata ============\n")
    print(json.dumps(metadata, indent=2))

    print("\n============ Nested ============\n")
    print(json.dumps(nested, indent=2))

    print("\n============ Flat ============\n")
    print(json.dumps(flat, indent=2))


if __name__ == "__main__":
    main()
