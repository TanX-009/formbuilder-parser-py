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
    form_json = load_json("onboarding.json")
    ans_json = load_json("test.json")
    bp_json = load_json("bp.json")
    answersWRTMetadata = {
        "service_ticket": {
            "company_name": ["asdf"],
            "document_type": ["invoice"],
            "service_type": ["out"],
        },
        "target_format": ["xrechnung"],
        "document_upload": [
            {
                "id": "58c380d9-818c-4b24-a4f3-53ced8a4858b",
                "file": {},
                "name": "test_13.pdf",
                "size": 33766,
                "language": "german",
                "type": "application/pdf",
                "url": "blob:http://localhost:5173/6aee5cdc-7224-4b25-8753-9fab2d91826a",
            },
            {
                "id": "5154d16f-b9f3-4c2f-a35f-91968690e058",
                "file": {},
                "name": "test_12.pdf",
                "size": 33766,
                "language": "german",
                "type": "application/pdf",
                "url": "blob:http://localhost:5173/e58bd97e-8076-42dd-86ec-a07c9f9ff117",
            },
            {
                "id": "278e8f50-4e92-4f5a-8e6b-2d5324be56ca",
                "file": {},
                "name": "test_11.pdf",
                "size": 33766,
                "language": "german",
                "type": "application/pdf",
                "url": "blob:http://localhost:5173/53ad9647-85e3-4979-8d10-1ba9dd7658a9",
            },
            {
                "id": "c03415f0-2329-47c7-9ab0-b1e0bd87c59c",
                "file": {},
                "name": "test_10.pdf",
                "size": 33766,
                "language": "german",
                "type": "application/pdf",
                "url": "blob:http://localhost:5173/46f1d86a-e2b5-411e-9578-099b6a41e276",
            },
            {
                "id": "c2333a59-30a7-4ea0-8780-fb54012e13f0",
                "file": {},
                "name": "test_7.pdf",
                "size": 33766,
                "language": "german",
                "type": "application/pdf",
                "url": "blob:http://localhost:5173/7e055498-02b4-4cec-b5be-a788dbaecd07",
            },
            {
                "id": "00d02941-8188-4612-bac9-2ee4b5dc8306",
                "file": {},
                "name": "test_6.pdf",
                "size": 33766,
                "language": "german",
                "type": "application/pdf",
                "url": "blob:http://localhost:5173/5ad053d5-c912-4388-8ba1-437244947926",
            },
            {
                "id": "d4aa1731-f507-42a6-a65e-7bd1bd3e4b65",
                "file": {},
                "name": "test_5.pdf",
                "size": 33766,
                "language": "german",
                "type": "application/pdf",
                "url": "blob:http://localhost:5173/7087ace2-547a-4e38-a4e4-975439853f1c",
            },
            {
                "id": "ad9d2b1d-5a9d-46ff-9b69-c4bd25374a6a",
                "file": {},
                "name": "test_4.pdf",
                "size": 33766,
                "language": "german",
                "type": "application/pdf",
                "url": "blob:http://localhost:5173/9982638a-92b2-425f-b6b5-5ef6c67e122b",
            },
        ],
        "recipient_info_from_email": ["no"],
        "recipient_info_from_pdf": ["no"],
        "doc_info_responsibility_by_bp": ["no"],
        "doc_info_responsibility_by_me": ["yes"],
        "out_doc_info_by_me": {
            "f614f3b4-d441-58a8-a6a8-65cecf97e703": {
                "original_to_recipient": ["yes"],
                "target_format": ["xrechnung"],
                "leitweg_id": ["asdf"],
                "peppol_id": ["asdf"],
                "delivery_channel": ["partner_email"],
                "recipient_email": ["asdf"],
            },
            "aad42f3b-96ca-5279-8163-7083e38b4921": {
                "original_to_recipient": ["yes"],
                "target_format": ["xrechnung"],
                "leitweg_id": ["dfaadfsadfsadfsasdfsadfasdfadfsdf"],
                "peppol_id": ["asdfasdfasdfasdfasdf"],
                "delivery_channel": ["partner_email"],
                "recipient_email": ["asdfasdfasdfasdfasdfasdfasdf"],
            },
        },
    }

    def get_bp():
        return bp_json

    async_map = {
        "/api/backend/general/business-partner/all?org_id=$${ORG_ID}$$": get_bp
    }

    metadata, nested, flat, possible, constructed = await walk_form(
        form_json, ans_json, answersWRTMetadata, async_map
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
    with open("constructed.json", "w", encoding="utf-8") as f:
        json.dump(constructed, f, ensure_ascii=False, indent=4)

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
