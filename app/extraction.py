import json
from datetime import date
from typing import Any

from openai import OpenAI

from app.config import get_settings
from app.db import add_possible_matches
from app.schemas import InteractionExtraction, RelationshipExtraction


def extraction_schema() -> dict[str, Any]:
    schema = RelationshipExtraction.model_json_schema()
    schema["additionalProperties"] = False
    return schema


def extract_relationships(note: str) -> tuple[RelationshipExtraction, list[str]]:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("Missing OPENAI_API_KEY.")

    note = note.strip()
    if not note:
        raise ValueError("Paste a note before extracting.")

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.openai_model,
        input=[
            {
                "role": "system",
                "content": "\n".join(
                    [
                        "You extract structured relationship data for a personal relationship manager.",
                        "This is not a sales CRM. Preserve human language.",
                        "Keep Knows About, Looking For, and Can Help With separate.",
                        "Use confidence=confirmed only when directly stated.",
                        "Use confidence=inferred for reasonable inference and uncertain when review is needed.",
                        "Use YYYY-MM-DD dates when explicit. Use null when a date is unknown.",
                        f"Current date: {date.today().isoformat()}.",
                        "Create stable temp_id values like person_1 and reference them from interactions and introductions.",
                        "Create an interaction record for the main person whenever possible.",
                        "Propose introductions only when the note clearly supports them.",
                    ]
                ),
            },
            {"role": "user", "content": note},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "relationship_extraction",
                "schema": extraction_schema(),
                "strict": False,
            }
        },
    )

    raw_text = response.output_text
    extraction = RelationshipExtraction.model_validate_json(raw_text)

    if extraction.people and not extraction.interactions:
        extraction.interactions.append(
            InteractionExtraction(
                person_temp_id=extraction.people[0].temp_id,
                summary=extraction.overall_summary or "Manual note",
                raw_text=note,
            )
        )

    warnings: list[str] = []
    try:
        extraction = add_possible_matches(extraction)
    except Exception as exc:
        warnings.append(f"Possible match lookup skipped: {exc}")

    return extraction, warnings


def extraction_to_json(extraction: RelationshipExtraction) -> str:
    return json.dumps(extraction.model_dump(mode="json"), indent=2)


def extraction_from_json(raw_json: str) -> RelationshipExtraction:
    return RelationshipExtraction.model_validate_json(raw_json)
