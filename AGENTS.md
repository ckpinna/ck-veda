Personal Relationship Manager

Project Purpose

This is a Python-first personal relationship manager and intro-routing engine.

The goal is to help the user understand:
	•	Who they know
	•	What each person knows about
	•	What each person is looking for
	•	What each person can help with
	•	Who should be introduced to whom
	•	Who is relevant for a given topic, geography, task, company, or opportunity
	•	Which relationships have become stale
	•	Which interactions, introductions, and sources created the most useful relationships

This is not a traditional sales CRM. It is a personal relationship graph optimized for memory, search, and high-quality introductions.

Stack

Use:
	•	Python
	•	FastAPI
	•	Pydantic
	•	Supabase Postgres
	•	Supabase migrations
	•	OpenAI structured extraction
	•	Simple HTML/Jinja or minimal frontend for MVP
	•	Streamlit is acceptable only for a quick prototype, but FastAPI should remain the core app

Do not use:
	•	Next.js for MVP
	•	Rust for MVP
	•	graph database for MVP
	•	email/text/WhatsApp integrations for MVP

Core Product Principles
	1.	Human-readable over enterprise CRM jargon.
	2.	Relationships are person-first, not company-first.
	3.	Supabase Postgres is the source of truth.
	4.	Every extracted fact should preserve enough context to remain useful later.
	5.	Start with manual text-based ingestion only.
	6.	Use explicit user-entered facts first.
	7.	Infer only when useful and mark inferred facts clearly.
	8.	Prefer simple relational tables first.
	9.	Do not create tables manually in Supabase. Schema changes should live in migrations.
	10.	Do not delete user data automatically.
	11.	When unsure whether to update an existing person or create a new person, surface for review instead of silently duplicating.

MVP Scope

The MVP should let the user paste a manual text note like:

Met Sarah at JPM. She is based in NYC, knows payments infra, is looking for seed fintech founders, and can help with Stripe intros. Ronak introduced us. We had a deep conversation about embedded finance. Best contact is LinkedIn.

The app should:
	1.	Extract structured relationship data with OpenAI.
	2.	Validate the extraction with Pydantic.
	3.	Show the user a review/edit screen.
	4.	Save approved data to Supabase.
	5.	Let the user search people by name, location, knows about, looking for, and can help with.
	6.	Show a person detail page.

Core Entities

People

One row per person.

Use a stable system-generated UUID. Do not use first name, last name, email, phone number, or LinkedIn as the primary identifier.

Fields:
	•	id
	•	display_name
	•	first_name
	•	last_name
	•	location
	•	current_context
	•	notes
	•	last_interaction_at
	•	created_at
	•	updated_at

Contact Methods

People can have multiple contact methods.

Fields:
	•	id
	•	person_id
	•	contact_type
	•	contact_value
	•	is_preferred
	•	label
	•	created_at
	•	updated_at

Allowed contact types:
	•	email
	•	personal_email
	•	work_email
	•	phone
	•	whatsapp
	•	linkedin
	•	twitter
	•	telegram
	•	signal
	•	other

Rules:
	•	Contact methods are not primary identifiers.
	•	A person may have multiple contact methods.
	•	One contact method can be preferred.
	•	Contact methods can help with identity resolution later.

Knows About

What a person understands, has experience with, or is meaningfully connected to.

This is not necessarily something they can actively help with.

Fields:
	•	id
	•	person_id
	•	topic
	•	context
	•	confidence
	•	mentioned_at
	•	last_confirmed_at
	•	status
	•	created_at
	•	updated_at

Examples:
	•	AI infrastructure
	•	Payments infrastructure
	•	Computational biology
	•	India fintech
	•	Enterprise SaaS procurement
	•	Biotech commercialization
	•	Developer tools

Looking For

Current asks, needs, or areas of demand from a person.

These should always be dated because asks decay quickly.

Fields:
	•	id
	•	person_id
	•	ask
	•	context
	•	asked_at
	•	last_confirmed_at
	•	status
	•	confidence
	•	created_at
	•	updated_at

Examples:
	•	Seed AI infra founders
	•	Fintech founders
	•	Customers in mid-market finance teams
	•	Expert on primate study design
	•	VP Sales candidates
	•	Co-investors for Series A rounds
	•	India fintech operators
	•	Angel investments

Rules:
	•	Every ask must have an asked_at date.
	•	If an ask is old, mark it stale rather than deleting it.
	•	Looking For is demand.

Can Help With

Actionable ways a person can help someone else.

This is supply.

Fields:
	•	id
	•	person_id
	•	help_area
	•	context
	•	confidence
	•	mentioned_at
	•	last_confirmed_at
	•	status
	•	created_at
	•	updated_at

Examples:
	•	Stripe introductions
	•	Databricks introductions
	•	AI infra technical diligence
	•	Hiring VP Engineering
	•	Fundraising advice
	•	Customer intros to CFOs
	•	GTM in India
	•	Biotech CRO introductions
	•	Founder referrals
	•	LP introductions
	•	Reviewing a data room
	•	Explaining FDA/regulatory strategy

Rules:
	•	Can Help With should be action-oriented.
	•	Do not confuse Knows About with Can Help With.
	•	Someone may know a topic but not be someone the user should ask for help.

Interactions

Meaningful touchpoints.

Fields:
	•	id
	•	person_id
	•	interaction_date
	•	channel
	•	summary
	•	raw_text
	•	interaction_quality
	•	created_at

Allowed channels:
	•	in_person
	•	email
	•	work_email
	•	text
	•	whatsapp
	•	phone
	•	zoom
	•	calendar
	•	manual_note
	•	other

Allowed interaction quality values:
	•	quick_hello
	•	normal_catch_up
	•	deep_conversation
	•	working_session
	•	trusted_conversation

Rules:
	•	Interaction summary should be concise but useful.
	•	Raw text may be stored when available.
	•	Interactions are the memory trail behind the relationship.

Introductions

Tracks intros made, requested, declined, ignored, or successful.

Fields:
	•	id
	•	from_person_id
	•	to_person_id
	•	requested_by_person_id
	•	reason
	•	status
	•	outcome
	•	intro_date
	•	created_at
	•	updated_at

Allowed status values:
	•	proposed
	•	requested
	•	made
	•	declined
	•	ignored
	•	successful
	•	closed

Rules:
	•	Introductions are core to the product.
	•	Track outcome when known.
	•	Intro history helps avoid overusing the same connectors.

Relationship Sources

Where or how the user met someone.

This is different from referrer.

Fields:
	•	id
	•	person_id
	•	source_type
	•	source_value
	•	source_date
	•	context
	•	created_at
	•	updated_at

Allowed source types:
	•	conference
	•	event
	•	community
	•	work
	•	school
	•	friend_group
	•	online
	•	cold_outreach
	•	founder_referral
	•	investor_referral
	•	other

Examples of source_value:
	•	JPM 2025
	•	NeurIPS 2026
	•	Seattle ski crew
	•	Argonautic
	•	Stanford
	•	Twitter
	•	LinkedIn
	•	India founder network

Referrals

Who introduced the user to a person.

This is different from relationship source.

Fields:
	•	id
	•	person_id
	•	referrer_person_id
	•	context
	•	referred_at
	•	created_at
	•	updated_at

Rules:
	•	Referrer should usually point to another person in People.
	•	If the referrer is unknown or not in the database yet, allow freeform context.

Confidence

Extracted facts should carry confidence.

Allowed values:
	•	confirmed
	•	inferred
	•	uncertain

Definitions:
	•	confirmed: directly stated by the user or source
	•	inferred: reasonable inference from context
	•	uncertain: possible but needs review

Default to confirmed only when the input clearly says it.

Staleness and Status

Relationship facts decay over time.

Allowed status values:
	•	active
	•	stale
	•	outdated
	•	archived

Use staleness especially for:
	•	Looking For
	•	Can Help With
	•	Knows About
	•	Current Context

Rules:
	•	Do not delete stale facts automatically.
	•	Mark them stale or outdated.
	•	The user can refresh or confirm later.

Groups and Communities

Do not require manual group tagging in MVP.

Groups should mostly emerge later as inferred clusters from:
	•	relationship sources
	•	referrers
	•	topics
	•	companies
	•	locations
	•	repeated interactions
	•	shared events

Examples:
	•	AI infra founders
	•	NYC fintech network
	•	Seattle outdoors friends
	•	India operators
	•	LP ecosystem
	•	Biotech experts

Do not implement clusters in MVP unless explicitly requested.

Matching Logic

The core matching engine should connect demand and supply.

Examples:
	•	Person A is looking for seed fintech founders.
	•	Person B can help with fintech founder referrals.
	•	Suggest an intro.
	•	Founder needs expert on primate study design.
	•	Person B knows about preclinical studies and can help with biotech CROs.
	•	Surface Person B as relevant.

Key query types:
	•	Who should I introduce this week?
	•	Who knows about X?
	•	Who is looking for Y?
	•	Who can help with Z?
	•	Who did I meet through Ronak?
	•	Who did I meet at JPM 2025?
	•	Who in SF have I not talked to recently?
	•	Which intros worked?
	•	Which environments generate the best relationships?

Extraction Rules

When ingesting a text note:
	1.	Identify people mentioned.
	2.	Match to existing people when possible.
	3.	If uncertain, propose a new person and flag for review.
	4.	Extract contact methods.
	5.	Extract location.
	6.	Extract current context.
	7.	Extract what the person knows about.
	8.	Extract what the person is looking for.
	9.	Extract what the person can help with.
	10.	Extract relationship source.
	11.	Extract referrer if present.
	12.	Create an interaction record.
	13.	Propose introductions only when the match is clear.
	14.	Never silently overwrite useful existing information.
	15.	Prefer appending new dated facts over replacing old facts unless the new fact clearly supersedes the old one.

Python Implementation Rules

Use Pydantic models for all structured extraction.

Suggested modules:
	•	app/main.py
	•	app/config.py
	•	app/db.py
	•	app/models.py
	•	app/schemas.py
	•	app/extraction.py
	•	app/routes/
	•	app/templates/
	•	supabase/migrations/

Use environment variables:
	•	OPENAI_API_KEY
	•	SUPABASE_URL
	•	SUPABASE_ANON_KEY
	•	SUPABASE_SERVICE_ROLE_KEY

Never commit .env.

Create .env.example.

API Routes

Initial API routes should include:
	•	GET /
	•	GET /people
	•	GET /people/{person_id}
	•	GET /ingest
	•	POST /api/extract
	•	POST /api/save-extraction
	•	GET /search

Keep the UI minimal.

Search

MVP search should cover:
	•	people.display_name
	•	people.location
	•	knows_about.topic
	•	looking_for.ask
	•	can_help_with.help_area
	•	interactions.summary

Use basic SQL search first. Do not implement vector search in MVP.

Naming Conventions

Use human language in the UI:
	•	People
	•	Contact Methods
	•	Knows About
	•	Looking For
	•	Can Help With
	•	Interactions
	•	Introductions
	•	Relationship Sources
	•	Referrals

Avoid enterprise CRM language:
	•	leads
	•	opportunities
	•	accounts
	•	pipeline
	•	deals

Database table names should be lowercase snake_case:
	•	people
	•	contact_methods
	•	knows_about
	•	looking_for
	•	can_help_with
	•	interactions
	•	introductions
	•	relationship_sources
	•	referrals

Agent Instructions

When working on this project:
	1.	Read this file before making product or schema decisions.
	2.	Preserve the human language of the product.
	3.	Do not introduce CRM jargon unless explicitly asked.
	4.	Keep the first implementation simple.
	5.	Prefer migrations over manual database edits.
	6.	Show proposed schema changes before applying them.
	7.	Do not modify production data without explicit approval.
	8.	Do not remove fields or delete data without explicit approval.
	9.	Maintain clear separation between:
	•	Knows About
	•	Looking For
	•	Can Help With
	•	Interactions
	•	Introductions
	10.	When creating extraction prompts, require structured JSON output and include confidence values.
	11.	When adding inferred fields, mark them as inferred.
	12.	Optimize for making useful introductions and retrieving relationship context quickly.
	13.	Use FastAPI and Pydantic as the core architecture.
	14.	Do not switch to Next.js unless explicitly requested.