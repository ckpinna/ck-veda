from datetime import date, datetime, timezone
from typing import Any, Optional

from supabase import Client, create_client

from app.config import get_settings
from app.schemas import PersonExtraction, RelationshipExtraction


def clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    trimmed = value.strip()
    return trimmed or None


def date_or_today(value: Optional[str]) -> str:
    return clean_text(value) or date.today().isoformat()


def date_or_none(value: Optional[str]) -> Optional[str]:
    return clean_text(value)


def get_supabase() -> Client:
    # MVP access note: all Supabase reads/writes go through FastAPI on the server.
    # SUPABASE_SERVICE_ROLE_KEY must never be exposed to browser code or templates.
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY.")
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def list_people(query: Optional[str] = None) -> list[dict[str, Any]]:
    supabase = get_supabase()
    if clean_text(query):
        return supabase.rpc("search_people", {"search_query": query}).execute().data or []

    return (
        supabase.table("people")
        .select("id,display_name,first_name,last_name,location,current_context,notes,last_interaction_at,created_at,updated_at")
        .order("last_interaction_at", desc=True, nullsfirst=False)
        .order("display_name")
        .execute()
        .data
        or []
    )


def get_person(person_id: str) -> Optional[dict[str, Any]]:
    rows = (
        get_supabase()
        .table("people")
        .select("*")
        .eq("id", person_id)
        .limit(1)
        .execute()
        .data
        or []
    )
    return rows[0] if rows else None


def get_person_detail(person_id: str) -> Optional[dict[str, Any]]:
    supabase = get_supabase()
    person = get_person(person_id)
    if not person:
        return None

    contact_methods = supabase.table("contact_methods").select("*").eq("person_id", person_id).execute().data or []
    knows_about = supabase.table("knows_about").select("*").eq("person_id", person_id).order("mentioned_at", desc=True).execute().data or []
    looking_for = supabase.table("looking_for").select("*").eq("person_id", person_id).order("asked_at", desc=True).execute().data or []
    can_help_with = supabase.table("can_help_with").select("*").eq("person_id", person_id).order("mentioned_at", desc=True).execute().data or []
    interactions = supabase.table("interactions").select("*").eq("person_id", person_id).order("interaction_date", desc=True).execute().data or []
    relationship_sources = supabase.table("relationship_sources").select("*").eq("person_id", person_id).order("source_date", desc=True).execute().data or []
    referrals = supabase.table("referrals").select("*").eq("person_id", person_id).order("referred_at", desc=True).execute().data or []

    intro_rows: list[dict[str, Any]] = []
    seen_intro_ids: set[str] = set()
    for column in ("from_person_id", "to_person_id", "requested_by_person_id"):
        rows = supabase.table("introductions").select("*").eq(column, person_id).execute().data or []
        for row in rows:
            if row["id"] not in seen_intro_ids:
                seen_intro_ids.add(row["id"])
                intro_rows.append(row)

    related_ids = {
        value
        for row in intro_rows
        for value in (row.get("from_person_id"), row.get("to_person_id"), row.get("requested_by_person_id"))
        if value
    }
    related_ids.update(row.get("referrer_person_id") for row in referrals if row.get("referrer_person_id"))
    people_by_id: dict[str, dict[str, Any]] = {}
    if related_ids:
        related = supabase.table("people").select("id,display_name,location,current_context").in_("id", list(related_ids)).execute().data or []
        people_by_id = {row["id"]: row for row in related}

    return {
        "person": person,
        "contact_methods": contact_methods,
        "knows_about": knows_about,
        "looking_for": looking_for,
        "can_help_with": can_help_with,
        "interactions": interactions,
        "introductions": sorted(intro_rows, key=lambda row: row.get("intro_date") or "", reverse=True),
        "relationship_sources": relationship_sources,
        "referrals": referrals,
        "people_by_id": people_by_id,
    }


def find_possible_matches(display_name: str) -> list[dict[str, Any]]:
    name = clean_text(display_name)
    if not name:
        return []
    return (
        get_supabase()
        .table("people")
        .select("id,display_name,location,current_context")
        .ilike("display_name", f"%{name}%")
        .limit(5)
        .execute()
        .data
        or []
    )


def add_possible_matches(extraction: RelationshipExtraction) -> RelationshipExtraction:
    people = []
    for person in extraction.people:
        person_data = person.model_dump(mode="json")
        person_data["selected_existing_person_id"] = None
        person_data["possible_matches"] = find_possible_matches(person.display_name)
        people.append(PersonExtraction.model_validate(person_data))
    return extraction.model_copy(update={"people": people})


def find_existing_person_by_name(display_name: Optional[str]) -> Optional[dict[str, Any]]:
    name = clean_text(display_name)
    if not name:
        return None
    rows = (
        get_supabase()
        .table("people")
        .select("id,display_name")
        .ilike("display_name", name)
        .limit(1)
        .execute()
        .data
        or []
    )
    return rows[0] if rows else None


def update_last_interaction(person_id: str, interaction_date: str) -> None:
    supabase = get_supabase()
    person = get_person(person_id)
    if not person:
        return
    current = person.get("last_interaction_at")
    if not current or current < interaction_date:
        supabase.table("people").update({"last_interaction_at": interaction_date}).eq("id", person_id).execute()


def person_has_preferred_contact(person_id: str) -> bool:
    rows = (
        get_supabase()
        .table("contact_methods")
        .select("id")
        .eq("person_id", person_id)
        .eq("is_preferred", True)
        .limit(1)
        .execute()
        .data
        or []
    )
    return bool(rows)


def insert_contact_method(person_id: str, item: Any, *, is_preferred: Optional[bool] = None) -> None:
    value = clean_text(item.contact_value)
    if not value:
        return
    supabase = get_supabase()
    existing = (
        supabase.table("contact_methods")
        .select("id")
        .eq("person_id", person_id)
        .eq("contact_type", item.contact_type.value)
        .eq("contact_value", value)
        .limit(1)
        .execute()
        .data
        or []
    )
    if existing:
        return
    supabase.table("contact_methods").insert(
        {
            "person_id": person_id,
            "contact_type": item.contact_type.value,
            "contact_value": value,
            "is_preferred": item.is_preferred if is_preferred is None else is_preferred,
            "label": clean_text(item.label),
            "confidence": item.confidence.value,
        }
    ).execute()


def resolve_person_id(
    temp_to_person_id: dict[str, str],
    name_to_person_id: dict[str, str],
    temp_id: Optional[str],
    name: Optional[str],
) -> Optional[str]:
    if clean_text(temp_id) and temp_id in temp_to_person_id:
        return temp_to_person_id[temp_id]
    name_key = clean_text(name)
    if name_key:
        return name_to_person_id.get(name_key.lower())
    return None


def save_extraction(extraction: RelationshipExtraction) -> dict[str, Any]:
    supabase = get_supabase()
    temp_to_person_id: dict[str, str] = {}
    name_to_person_id: dict[str, str] = {}
    saved_people: list[dict[str, Any]] = []

    for person in extraction.people:
        person_id = clean_text(person.selected_existing_person_id)
        reused_existing = bool(person_id)

        if not person_id:
            inserted = (
                supabase.table("people")
                .insert(
                    {
                        "display_name": person.display_name,
                        "first_name": clean_text(person.first_name),
                        "last_name": clean_text(person.last_name),
                        "location": clean_text(person.location),
                        "location_confidence": person.location_confidence.value,
                        "current_context": clean_text(person.current_context),
                        "current_context_confidence": person.current_context_confidence.value,
                        "current_context_status": person.current_context_status.value,
                        "notes": clean_text(person.notes),
                    }
                )
                .execute()
                .data
                or []
            )
            person_id = inserted[0]["id"]

        temp_to_person_id[person.temp_id] = person_id
        name_to_person_id[person.display_name.lower()] = person_id
        saved_people.append({"id": person_id, "display_name": person.display_name, "reused_existing": reused_existing})

        save_person_facts(person_id, person)

    for interaction in extraction.interactions:
        person_id = temp_to_person_id.get(interaction.person_temp_id)
        summary = clean_text(interaction.summary)
        if not person_id or not summary:
            continue
        interaction_date = date_or_today(interaction.interaction_date)
        supabase.table("interactions").insert(
            {
                "person_id": person_id,
                "interaction_date": interaction_date,
                "channel": interaction.channel.value,
                "summary": summary,
                "raw_text": clean_text(interaction.raw_text),
                "interaction_quality": interaction.interaction_quality.value,
                "confidence": interaction.confidence.value,
            }
        ).execute()
        update_last_interaction(person_id, interaction_date)

    for intro in extraction.possible_introductions:
        from_person_id = resolve_person_id(temp_to_person_id, name_to_person_id, intro.from_person_temp_id, intro.from_person_name)
        to_person_id = resolve_person_id(temp_to_person_id, name_to_person_id, intro.to_person_temp_id, intro.to_person_name)
        reason = clean_text(intro.reason)
        if not from_person_id or not to_person_id or from_person_id == to_person_id or not reason:
            continue
        requested_by_person_id = resolve_person_id(
            temp_to_person_id,
            name_to_person_id,
            intro.requested_by_person_temp_id,
            intro.requested_by_person_name,
        )
        supabase.table("introductions").insert(
            {
                "from_person_id": from_person_id,
                "to_person_id": to_person_id,
                "requested_by_person_id": requested_by_person_id,
                "reason": reason,
                "status": intro.status.value,
                "outcome": clean_text(intro.outcome),
                "intro_date": date_or_today(intro.intro_date),
                "confidence": intro.confidence.value,
            }
        ).execute()

    return {"saved_people": saved_people, "saved_at": datetime.now(timezone.utc).isoformat()}


def save_person_facts(person_id: str, person: PersonExtraction) -> None:
    supabase = get_supabase()
    has_preferred_contact = person_has_preferred_contact(person_id)

    for contact_method in person.contact_methods:
        is_preferred = contact_method.is_preferred and not has_preferred_contact
        insert_contact_method(person_id, contact_method, is_preferred=is_preferred)
        has_preferred_contact = has_preferred_contact or is_preferred

    knows_about_rows = [
        {
            "person_id": person_id,
            "topic": item.topic,
            "context": clean_text(item.context),
            "confidence": item.confidence.value,
            "mentioned_at": date_or_today(item.mentioned_at),
            "last_confirmed_at": date_or_none(item.last_confirmed_at),
            "status": item.status.value,
        }
        for item in person.knows_about
        if clean_text(item.topic)
    ]
    if knows_about_rows:
        supabase.table("knows_about").insert(knows_about_rows).execute()

    looking_for_rows = [
        {
            "person_id": person_id,
            "ask": item.ask,
            "context": clean_text(item.context),
            "asked_at": date_or_today(item.asked_at),
            "last_confirmed_at": date_or_none(item.last_confirmed_at),
            "status": item.status.value,
            "confidence": item.confidence.value,
        }
        for item in person.looking_for
        if clean_text(item.ask)
    ]
    if looking_for_rows:
        supabase.table("looking_for").insert(looking_for_rows).execute()

    can_help_rows = [
        {
            "person_id": person_id,
            "help_area": item.help_area,
            "context": clean_text(item.context),
            "confidence": item.confidence.value,
            "mentioned_at": date_or_today(item.mentioned_at),
            "last_confirmed_at": date_or_none(item.last_confirmed_at),
            "status": item.status.value,
        }
        for item in person.can_help_with
        if clean_text(item.help_area)
    ]
    if can_help_rows:
        supabase.table("can_help_with").insert(can_help_rows).execute()

    if person.relationship_source and (clean_text(person.relationship_source.source_value) or clean_text(person.relationship_source.context)):
        source = person.relationship_source
        supabase.table("relationship_sources").insert(
            {
                "person_id": person_id,
                "source_type": source.source_type.value,
                "source_value": clean_text(source.source_value),
                "source_date": date_or_today(source.source_date),
                "context": clean_text(source.context),
                "confidence": source.confidence.value,
            }
        ).execute()

    if person.referrer and (clean_text(person.referrer.display_name) or clean_text(person.referrer.context)):
        existing_referrer = find_existing_person_by_name(person.referrer.display_name)
        context_parts = [clean_text(person.referrer.context)]
        if not existing_referrer and clean_text(person.referrer.display_name):
            context_parts.append(f"Referrer name mentioned: {person.referrer.display_name}")
        supabase.table("referrals").insert(
            {
                "person_id": person_id,
                "referrer_person_id": existing_referrer["id"] if existing_referrer else None,
                "context": " ".join(part for part in context_parts if part),
                "referred_at": date_or_today(person.referrer.referred_at),
                "confidence": person.referrer.confidence.value,
            }
        ).execute()
