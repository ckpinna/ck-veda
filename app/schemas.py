from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Confidence(StrEnum):
    confirmed = "confirmed"
    inferred = "inferred"
    uncertain = "uncertain"


class RelationshipStatus(StrEnum):
    active = "active"
    stale = "stale"
    outdated = "outdated"
    archived = "archived"


class ContactType(StrEnum):
    email = "email"
    personal_email = "personal_email"
    work_email = "work_email"
    phone = "phone"
    whatsapp = "whatsapp"
    linkedin = "linkedin"
    twitter = "twitter"
    telegram = "telegram"
    signal = "signal"
    other = "other"


class InteractionChannel(StrEnum):
    in_person = "in_person"
    email = "email"
    work_email = "work_email"
    text = "text"
    whatsapp = "whatsapp"
    phone = "phone"
    zoom = "zoom"
    calendar = "calendar"
    manual_note = "manual_note"
    other = "other"


class InteractionQuality(StrEnum):
    quick_hello = "quick_hello"
    normal_catch_up = "normal_catch_up"
    deep_conversation = "deep_conversation"
    working_session = "working_session"
    trusted_conversation = "trusted_conversation"


class IntroductionStatus(StrEnum):
    proposed = "proposed"
    requested = "requested"
    made = "made"
    declined = "declined"
    ignored = "ignored"
    successful = "successful"
    closed = "closed"


class SourceType(StrEnum):
    conference = "conference"
    event = "event"
    community = "community"
    work = "work"
    school = "school"
    friend_group = "friend_group"
    online = "online"
    cold_outreach = "cold_outreach"
    founder_referral = "founder_referral"
    investor_referral = "investor_referral"
    other = "other"


class AppModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PossibleMatch(AppModel):
    id: str
    display_name: str
    location: str | None = None
    current_context: str | None = None


class ContactMethodExtraction(AppModel):
    contact_type: ContactType = ContactType.other
    contact_value: str
    is_preferred: bool = False
    label: str | None = None
    confidence: Confidence = Confidence.uncertain


class KnowsAboutExtraction(AppModel):
    topic: str
    context: str | None = None
    confidence: Confidence = Confidence.uncertain
    mentioned_at: str | None = Field(default=None, description="YYYY-MM-DD when known.")
    last_confirmed_at: str | None = Field(default=None, description="YYYY-MM-DD when known.")
    status: RelationshipStatus = RelationshipStatus.active


class LookingForExtraction(AppModel):
    ask: str
    context: str | None = None
    asked_at: str | None = Field(default=None, description="YYYY-MM-DD when known.")
    last_confirmed_at: str | None = Field(default=None, description="YYYY-MM-DD when known.")
    status: RelationshipStatus = RelationshipStatus.active
    confidence: Confidence = Confidence.uncertain


class CanHelpWithExtraction(AppModel):
    help_area: str
    context: str | None = None
    confidence: Confidence = Confidence.uncertain
    mentioned_at: str | None = Field(default=None, description="YYYY-MM-DD when known.")
    last_confirmed_at: str | None = Field(default=None, description="YYYY-MM-DD when known.")
    status: RelationshipStatus = RelationshipStatus.active


class RelationshipSourceExtraction(AppModel):
    source_type: SourceType = SourceType.other
    source_value: str | None = None
    source_date: str | None = Field(default=None, description="YYYY-MM-DD when known.")
    context: str | None = None
    confidence: Confidence = Confidence.uncertain


class ReferrerExtraction(AppModel):
    display_name: str | None = None
    context: str | None = None
    referred_at: str | None = Field(default=None, description="YYYY-MM-DD when known.")
    confidence: Confidence = Confidence.uncertain


class PersonExtraction(AppModel):
    temp_id: str
    display_name: str
    first_name: str | None = None
    last_name: str | None = None
    location: str | None = None
    location_confidence: Confidence = Confidence.uncertain
    current_context: str | None = None
    current_context_confidence: Confidence = Confidence.uncertain
    current_context_status: RelationshipStatus = RelationshipStatus.active
    notes: str | None = None
    confidence: Confidence = Confidence.uncertain
    selected_existing_person_id: str | None = None
    possible_matches: list[PossibleMatch] = Field(default_factory=list)
    contact_methods: list[ContactMethodExtraction] = Field(default_factory=list)
    knows_about: list[KnowsAboutExtraction] = Field(default_factory=list)
    looking_for: list[LookingForExtraction] = Field(default_factory=list)
    can_help_with: list[CanHelpWithExtraction] = Field(default_factory=list)
    relationship_source: RelationshipSourceExtraction | None = None
    referrer: ReferrerExtraction | None = None


class InteractionExtraction(AppModel):
    person_temp_id: str
    interaction_date: str | None = Field(default=None, description="YYYY-MM-DD when known.")
    channel: InteractionChannel = InteractionChannel.manual_note
    summary: str
    raw_text: str | None = None
    interaction_quality: InteractionQuality = InteractionQuality.normal_catch_up
    confidence: Confidence = Confidence.uncertain


class PossibleIntroductionExtraction(AppModel):
    from_person_temp_id: str | None = None
    to_person_temp_id: str | None = None
    from_person_name: str | None = None
    to_person_name: str | None = None
    requested_by_person_temp_id: str | None = None
    requested_by_person_name: str | None = None
    reason: str
    status: IntroductionStatus = IntroductionStatus.proposed
    outcome: str | None = None
    intro_date: str | None = Field(default=None, description="YYYY-MM-DD when known.")
    confidence: Confidence = Confidence.uncertain


class RelationshipExtraction(AppModel):
    people: list[PersonExtraction] = Field(default_factory=list)
    interactions: list[InteractionExtraction] = Field(default_factory=list)
    possible_introductions: list[PossibleIntroductionExtraction] = Field(default_factory=list)
    overall_summary: str | None = None


class SaveResult(AppModel):
    saved_people: list[dict[str, Any]]
