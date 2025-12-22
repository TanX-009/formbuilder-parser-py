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
        "service_ticket": {
            "company_name": ["asdf"],
            "document_type": ["invoice"],
            "service_type": ["in"],
        },
        "checkout_format": ["xrechnung"],
        "in_doc_info_by_bp": {
            "6b2fc1e7-b6cb-4234-9f05-772d75ad73de": {
                "checkin_format": ["pdf"],
                "checkin_channel": ["email"],
                "responsible_person_at_bp": ["asdf"],
                "email_of_responsible_person_at_bp": ["sadf"],
            },
            "e8117d11-0b80-41f2-bb28-dff05250657f": {
                "checkin_format": ["pdf"],
                "checkin_channel": ["email"],
                "responsible_person_at_bp": ["asdfasdf"],
                "email_of_responsible_person_at_bp": ["123445443"],
            },
        },
        "in_doc_info_by_me": {
            "6b2fc1e7-b6cb-4234-9f05-772d75ad73de": {
                "checkin_format": ["pdf"],
                "checkin_channel": ["email"],
                "document_upload": [
                    {
                        "id": "fd84a557-228b-4d5c-90e0-ea9dd8d7b674",
                        "file": {},
                        "name": "test_17.pdf",
                        "size": 33766,
                        "language": "german",
                        "type": "application/pdf",
                        "url": "blob:http://localhost:5173/2c562e37-a512-4588-bf81-c4391744ac56",
                    },
                    {
                        "id": "12599738-028d-485d-8d10-8d4f35afee27",
                        "file": {},
                        "name": "test_16.pdf",
                        "size": 33766,
                        "language": "german",
                        "type": "application/pdf",
                        "url": "blob:http://localhost:5173/49fe03a2-26a9-49f7-bdd3-88fca3860b9f",
                    },
                    {
                        "id": "fd19f02e-aa58-4719-b99d-95dba39c2a55",
                        "file": {},
                        "name": "test_15.pdf",
                        "size": 33766,
                        "language": "german",
                        "type": "application/pdf",
                        "url": "blob:http://localhost:5173/782d4734-c1a7-4de0-a957-9c0b7895efad",
                    },
                    {
                        "id": "ca8b3d4f-436c-4aef-a4a3-01184dadcdc6",
                        "file": {},
                        "name": "test_14.pdf",
                        "size": 33766,
                        "language": "german",
                        "type": "application/pdf",
                        "url": "blob:http://localhost:5173/425fd301-31ec-4eb7-830b-81bd22de3688",
                    },
                    {
                        "id": "66b6d4f9-28e6-421c-8895-bf674fcb9582",
                        "file": {},
                        "name": "test_13.pdf",
                        "size": 33766,
                        "language": "german",
                        "type": "application/pdf",
                        "url": "blob:http://localhost:5173/d64bf1a1-a3e3-4425-bda6-a0ab919d7b27",
                    },
                    {
                        "id": "b6e4136b-66de-4b1f-8e86-d858023844ed",
                        "file": {},
                        "name": "test_12.pdf",
                        "size": 33766,
                        "language": "german",
                        "type": "application/pdf",
                        "url": "blob:http://localhost:5173/a68e7ef6-88b7-492e-87a2-eed971ce6aa7",
                    },
                    {
                        "id": "c697107c-fa82-476d-951f-9c901ce703b4",
                        "file": {},
                        "name": "test_11.pdf",
                        "size": 33766,
                        "language": "german",
                        "type": "application/pdf",
                        "url": "blob:http://localhost:5173/92cad2f7-6027-4969-b74c-f71360b1db4d",
                    },
                    {
                        "id": "7dd535b5-2b95-46b9-b079-b314e704d06c",
                        "file": {},
                        "name": "test_10.pdf",
                        "size": 33766,
                        "language": "german",
                        "type": "application/pdf",
                        "url": "blob:http://localhost:5173/6a935c6a-8c9c-4b57-8499-76f06b707f2a",
                    },
                    {
                        "id": "a68b0fb6-0c2a-473d-8460-77c33ff6068e",
                        "file": {},
                        "name": "test_9.pdf",
                        "size": 33766,
                        "language": "german",
                        "type": "application/pdf",
                        "url": "blob:http://localhost:5173/acb6c29f-6b41-47f7-b3d1-f65f627e7a9b",
                    },
                    {
                        "id": "ff709562-b4cd-4eb3-9316-92d2b05cd6be",
                        "file": {},
                        "name": "test_8.pdf",
                        "size": 33766,
                        "language": "german",
                        "type": "application/pdf",
                        "url": "blob:http://localhost:5173/f96dae9e-5781-4baa-8f1a-4573551bbc36",
                    },
                    {
                        "id": "beb20601-0287-4ce9-9745-2769ea146d65",
                        "file": {},
                        "name": "test_7.pdf",
                        "size": 33766,
                        "language": "german",
                        "type": "application/pdf",
                        "url": "blob:http://localhost:5173/640a7006-4034-4398-9b56-854d5f0ed897",
                    },
                    {
                        "id": "9643c4cc-93f7-402d-8123-383ce1cd8539",
                        "file": {},
                        "name": "test_6.pdf",
                        "size": 33766,
                        "language": "german",
                        "type": "application/pdf",
                        "url": "blob:http://localhost:5173/e1d5d9b2-b681-4c04-940e-8c29ca462fb3",
                    },
                    {
                        "id": "f5343314-3508-410a-aea8-df3358593099",
                        "file": {},
                        "name": "test_5.pdf",
                        "size": 33766,
                        "language": "german",
                        "type": "application/pdf",
                        "url": "blob:http://localhost:5173/3b1ea212-7f95-4d15-b52f-c5c75f279217",
                    },
                    {
                        "id": "187ff911-7e5a-464a-a691-1faad2621a09",
                        "file": {},
                        "name": "test_4.pdf",
                        "size": 33766,
                        "language": "german",
                        "type": "application/pdf",
                        "url": "blob:http://localhost:5173/e0278c28-4fb5-4aac-a485-b2f4083ca2c2",
                    },
                ],
            }
        },
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
