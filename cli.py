import sys
import json
import asyncio
from pathlib import Path

from form.form import walk_form


def load_json(file_path: str):
    """Load and return JSON from a file path."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


async def main():
    if len(sys.argv) != 3:
        print("Usage: python main.py <form_definition.json> <answers.json>")
        sys.exit(1)

    form_file = sys.argv[1]
    ans_file = sys.argv[2]

    # answers = test_all_inclusive.get("answers")
    # servic_type = test_all_inclusive.get("service_type")
    # print(servic_type)
    # bps = test_all_inclusive.get("business_partners")
    # print(bps, len(bps))

    form_json = load_json(form_file)
    ans_json = load_json(ans_file)
    answersWRTMetadata = {
        "service_ticket": {"document_type": ["asdf"]},
    }

    metadata, nested, flat, possible, constructed = await walk_form(
        form_json, ans_json, answersWRTMetadata
    )

    print("\n============ Metadata ============\n")
    print(json.dumps(metadata, indent=2))
    #
    # print("\n============ Nested ============\n")
    # print(json.dumps(nested, indent=2))
    #
    # print("\n============ Flat ============\n")
    # print(json.dumps(flat, indent=2))
    #
    # print("\n============ Possible ============\n")
    # print(json.dumps(possible, indent=2))
    #
    # print("\n============ Constructed ============\n")
    # print(json.dumps(constructed, indent=2))
    # with open("constructed.json", "w", encoding="utf-8") as f:
    #     json.dump(constructed, f, ensure_ascii=False, indent=4)

    # if servic_type == "in":
    #     form_json = load_json("form_in_bp_ui.json")
    #     bps = test_all_inclusive.get("business_partners")
    #
    #     for bp in bps:
    #         bp_answers = bp.get("answers")
    #     metadata, nested, flat, possible, constructed = walk_form(
    #         form_json, bp_answers, {}
    #     )
    #
    #     print(json.dumps(nested, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
