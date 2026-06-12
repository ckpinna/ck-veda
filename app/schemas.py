from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class Confidence(str, Enum):
    confirmed = "confirmed"
    inferred = "inferred"
    uncertain = "uncertain"


class RelationshipStatus(str, Enum):
    active = "active"
    stale = "stale"
    outdated = "outdated"
    archived = "archived"


class ContactType(str, Enum):
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


class InteractionChannel(str, Enum):
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


class InteractionQuality(str, Enum):
    quick_hello = "quick_hello"
    normal_catch_up = "normal_catch_up"
    deep_conversation = "deep_conversation"
    working_session = "working_session"
    trusted_conversation = "trusted_conversation"


class IntroductionStatus(str, Enum):
    proposed = "proposed"
    requested = "requested"
    made = "made"
    declined = "declined"
    ignored = "ignored"
    successful = "successful"
    closed = "closed"


class SourceType(str, Enum):
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
    location: Optional[str] = None
    current_context: Optional[str] = None


class ContactMethodExtraction(AppModel):
    contact_type: ContactType = ContactType.other
    contact_value: str
    is_preferred: bool = False
    label: Optional[str] = None
    confidence: Confidence = Confidence.uncertain


class KnowsAboutExtraction(AppModel):
    topic: str
    context: Optional[str] = None
    confidence: Confidence = Confidence.uncertain
    mentioned_at: Optional[str] = Field(default=None, description="YYYY-MM-DD when known.")
    last_confirmed_at: Optional[str] = Field(default=None, description="YYYY-MM-DD when known.")
    status: RelationshipStatus = RelationshipStatus.active


class LookingForExtraction(AppModel):
    ask: str
    context: Optional[str] = None
    asked_at: Optional[str] = Field(default=None, description="YYYY-MM-DD when known.")
    last_confirmed_at: Optional[str] = Field(default=None, description="YYYY-MM-DD when known.")
    status: RelationshipStatus = RelationshipStatus.active
    confidence: Confidence = Confidence.uncertain


class CanHelpWithExtraction(AppModel):
    help_area: str
    context: Optional[str] = None
    confidence: Confidence = Confidence.uncertain
    mentioned_at: Optional[str] = Field(default=None, description="YYYY-MM-DD when known.")
    last_confirmed_at: Optional[str] = Field(default=None, description="YYYY-MM-DD when known.")
    status: RelationshipStatus = RelationshipStatus.active


class RelationshipSourceExtraction(AppModel):
    source_type: SourceType = SourceType.other
    source_value: Optional[str] = None
    source_date: Optional[str] = Field(default=None, description="YYYY-MM-DD when known.")
    context: Optional[str] = None
    confidence: Confidence = Confidence.uncertain


class ReferrerExtraction(AppModel):
    display_name: Optional[str] = None
    context: Optional[str] = None
    referred_at: Optional[str] = Field(default=None, description="YYYY-MM-DD when known.")
    confidence: Confidence = Confidence.uncertain


class PersonExtraction(AppModel):
    temp_id: str
    display_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    location_confidence: Confidence = Confidence.uncertain
    current_context: Optional[str] = None
    current_context_confidence: Confidence = Confidence.uncertain
    current_context_status: RelationshipStatus = RelationshipStatus.active
    notes: Optional[str] = None
    confidence: Confidence = Confidence.uncertain
    selected_existing_person_id: Optional[str] = None
    possible_matches: list[PossibleMatch] = Field(default_factory=list)
    contact_methods: list[ContactMethodExtraction] = Field(default_factory=list)
    knows_about: list[KnowsAboutExtraction] = Field(default_factory=list)
    looking_for: list[LookingForExtraction] = Field(default_factory=list)
    can_help_with: list[CanHelpWithExtraction] = Field(default_factory=list)
    relationship_source: Optional[RelationshipSourceExtraction] = None
    referrer: Optional[ReferrerExtraction] = None


class InteractionExtraction(AppModel):
    person_temp_id: str
    interaction_date: Optional[str] = Field(default=None, description="YYYY-MM-DD when known.")
    channel: InteractionChannel = InteractionChannel.manual_note
    summary: str
    raw_text: Optional[str] = None
    interaction_quality: InteractionQuality = InteractionQuality.normal_catch_up
    confidence: Confidence = Confidence.uncertain


class PossibleIntroductionExtraction(AppModel):
    from_person_temp_id: Optional[str] = None
    to_person_temp_id: Optional[str] = None
    from_person_name: Optional[str] = None
    to_person_name: Optional[str] = None
    requested_by_person_temp_id: Optional[str] = None
    requested_by_person_name: Optional[str] = None
    reason: str
    status: IntroductionStatus = IntroductionStatus.proposed
    outcome: Optional[str] = None
    intro_date: Optional[str] = Field(default=None, description="YYYY-MM-DD when known.")
    confidence: Confidence = Confidence.uncertain


class RelationshipExtraction(AppModel):
    people: list[PersonExtraction] = Field(default_factory=list)
    interactions: list[InteractionExtraction] = Field(default_factory=list)
    possible_introductions: list[PossibleIntroductionExtraction] = Field(default_factory=list)
    overall_summary: Optional[str] = None


class SaveResult(AppModel):
    saved_people: list[dict[str, Any]]
