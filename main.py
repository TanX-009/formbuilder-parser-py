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
    ans_json = load_json("ans_in.json")
    answersWRTMetadata = {
        "service_ticket": {"document_type": ["asdf"]},
    }

    def get_bp():
        return {
            "code": 200,
            "data": [
                {
                    "uuid": "6b2fc1e7-b6cb-4234-9f05-772d75ad73de",
                    "company_name": "test",
                    "vat_id": "test",
                    "customer_number": None,
                    "original_to_recipient": None,
                    "delivery_channel": None,
                    "leitweg_id": None,
                    "responsible_person_at_bp": None,
                    "email_of_responsible_person_at_bp": None,
                    "checkin_format": None,
                    "checkin_channel": None,
                    "senders_email": None,
                    "service_ticket_id": None,
                    "supedio_id": None,
                    "avatar": None,
                    "business_id_num": "etset",
                    "gln": 1234567890123,
                    "is_referred": False,
                    "completed": False,
                    "invite_link": None,
                    "invite_data": None,
                    "submission_status": None,
                    "file_uuids": None,
                    "id": 3,
                    "file_data": None,
                    "organization_id": None,
                    "partner_type": "supplier",
                },
                {
                    "uuid": "e8117d11-0b80-41f2-bb28-dff05250657f",
                    "company_name": "tttt",
                    "vat_id": "asdf",
                    "customer_number": None,
                    "original_to_recipient": None,
                    "delivery_channel": None,
                    "leitweg_id": None,
                    "responsible_person_at_bp": None,
                    "email_of_responsible_person_at_bp": None,
                    "checkin_format": None,
                    "checkin_channel": None,
                    "senders_email": None,
                    "service_ticket_id": None,
                    "supedio_id": None,
                    "avatar": None,
                    "business_id_num": "asdf",
                    "gln": 1234567890123,
                    "is_referred": False,
                    "completed": False,
                    "invite_link": None,
                    "invite_data": None,
                    "submission_status": None,
                    "file_uuids": None,
                    "id": 4,
                    "file_data": None,
                    "organization_id": None,
                    "partner_type": "supplier",
                },
            ],
            "message": "Operation completed successfully",
        }

    async_map = {"/api/backend/general/business-partner/all": get_bp}

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
