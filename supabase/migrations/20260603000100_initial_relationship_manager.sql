create extension if not exists pgcrypto with schema extensions;

do $$
begin
  create type public.confidence_level as enum ('confirmed', 'inferred', 'uncertain');
exception
  when duplicate_object then null;
end $$;

do $$
begin
  create type public.relationship_status as enum ('active', 'stale', 'outdated', 'archived');
exception
  when duplicate_object then null;
end $$;

do $$
begin
  create type public.contact_method_type as enum (
    'email',
    'personal_email',
    'work_email',
    'phone',
    'whatsapp',
    'linkedin',
    'twitter',
    'telegram',
    'signal',
    'other'
  );
exception
  when duplicate_object then null;
end $$;

do $$
begin
  create type public.interaction_channel as enum (
    'in_person',
    'email',
    'work_email',
    'text',
    'whatsapp',
    'phone',
    'zoom',
    'calendar',
    'manual_note',
    'other'
  );
exception
  when duplicate_object then null;
end $$;

do $$
begin
  create type public.interaction_quality as enum (
    'quick_hello',
    'normal_catch_up',
    'deep_conversation',
    'working_session',
    'trusted_conversation'
  );
exception
  when duplicate_object then null;
end $$;

do $$
begin
  create type public.introduction_status as enum (
    'proposed',
    'requested',
    'made',
    'declined',
    'ignored',
    'successful',
    'closed'
  );
exception
  when duplicate_object then null;
end $$;

do $$
begin
  create type public.relationship_source_type as enum (
    'conference',
    'event',
    'community',
    'work',
    'school',
    'friend_group',
    'online',
    'cold_outreach',
    'founder_referral',
    'investor_referral',
    'other'
  );
exception
  when duplicate_object then null;
end $$;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table public.people (
  id uuid primary key default gen_random_uuid(),
  display_name text not null,
  first_name text,
  last_name text,
  location text,
  location_confidence public.confidence_level not null default 'uncertain',
  current_context text,
  current_context_confidence public.confidence_level not null default 'uncertain',
  current_context_status public.relationship_status not null default 'active',
  notes text,
  last_interaction_at date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint people_display_name_not_blank check (length(btrim(display_name)) > 0)
);

create table public.contact_methods (
  id uuid primary key default gen_random_uuid(),
  person_id uuid not null references public.people(id) on delete cascade,
  contact_type public.contact_method_type not null default 'other',
  contact_value text not null,
  is_preferred boolean not null default false,
  label text,
  confidence public.confidence_level not null default 'uncertain',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint contact_methods_value_not_blank check (length(btrim(contact_value)) > 0)
);

create table public.knows_about (
  id uuid primary key default gen_random_uuid(),
  person_id uuid not null references public.people(id) on delete cascade,
  topic text not null,
  context text,
  confidence public.confidence_level not null default 'uncertain',
  mentioned_at date not null default current_date,
  last_confirmed_at date,
  status public.relationship_status not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint knows_about_topic_not_blank check (length(btrim(topic)) > 0)
);

create table public.looking_for (
  id uuid primary key default gen_random_uuid(),
  person_id uuid not null references public.people(id) on delete cascade,
  ask text not null,
  context text,
  asked_at date not null default current_date,
  last_confirmed_at date,
  status public.relationship_status not null default 'active',
  confidence public.confidence_level not null default 'uncertain',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint looking_for_ask_not_blank check (length(btrim(ask)) > 0)
);

create table public.can_help_with (
  id uuid primary key default gen_random_uuid(),
  person_id uuid not null references public.people(id) on delete cascade,
  help_area text not null,
  context text,
  confidence public.confidence_level not null default 'uncertain',
  mentioned_at date not null default current_date,
  last_confirmed_at date,
  status public.relationship_status not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint can_help_with_area_not_blank check (length(btrim(help_area)) > 0)
);

create table public.interactions (
  id uuid primary key default gen_random_uuid(),
  person_id uuid not null references public.people(id) on delete cascade,
  interaction_date date not null default current_date,
  channel public.interaction_channel not null default 'manual_note',
  summary text not null,
  raw_text text,
  interaction_quality public.interaction_quality not null default 'normal_catch_up',
  confidence public.confidence_level not null default 'uncertain',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint interactions_summary_not_blank check (length(btrim(summary)) > 0)
);

create table public.introductions (
  id uuid primary key default gen_random_uuid(),
  from_person_id uuid not null references public.people(id) on delete restrict,
  to_person_id uuid not null references public.people(id) on delete restrict,
  requested_by_person_id uuid references public.people(id) on delete set null,
  reason text,
  status public.introduction_status not null default 'proposed',
  outcome text,
  intro_date date not null default current_date,
  confidence public.confidence_level not null default 'uncertain',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint introductions_people_are_distinct check (from_person_id <> to_person_id)
);

create table public.relationship_sources (
  id uuid primary key default gen_random_uuid(),
  person_id uuid not null references public.people(id) on delete cascade,
  source_type public.relationship_source_type not null default 'other',
  source_value text,
  source_date date not null default current_date,
  context text,
  confidence public.confidence_level not null default 'uncertain',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.referrals (
  id uuid primary key default gen_random_uuid(),
  person_id uuid not null references public.people(id) on delete cascade,
  referrer_person_id uuid references public.people(id) on delete set null,
  context text,
  referred_at date not null default current_date,
  confidence public.confidence_level not null default 'uncertain',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint referrals_person_not_referrer check (
    referrer_person_id is null or person_id <> referrer_person_id
  )
);

create trigger set_people_updated_at
before update on public.people
for each row execute function public.set_updated_at();

create trigger set_contact_methods_updated_at
before update on public.contact_methods
for each row execute function public.set_updated_at();

create trigger set_knows_about_updated_at
before update on public.knows_about
for each row execute function public.set_updated_at();

create trigger set_looking_for_updated_at
before update on public.looking_for
for each row execute function public.set_updated_at();

create trigger set_can_help_with_updated_at
before update on public.can_help_with
for each row execute function public.set_updated_at();

create trigger set_interactions_updated_at
before update on public.interactions
for each row execute function public.set_updated_at();

create trigger set_introductions_updated_at
before update on public.introductions
for each row execute function public.set_updated_at();

create trigger set_relationship_sources_updated_at
before update on public.relationship_sources
for each row execute function public.set_updated_at();

create trigger set_referrals_updated_at
before update on public.referrals
for each row execute function public.set_updated_at();

create index people_display_name_idx on public.people (display_name);
create index people_location_idx on public.people (location);
create index people_last_interaction_at_idx on public.people (last_interaction_at desc);
create index people_search_idx on public.people using gin (
  to_tsvector(
    'simple',
    coalesce(display_name, '') || ' ' ||
    coalesce(first_name, '') || ' ' ||
    coalesce(last_name, '') || ' ' ||
    coalesce(location, '') || ' ' ||
    coalesce(current_context, '') || ' ' ||
    coalesce(notes, '')
  )
);

create index contact_methods_person_id_idx on public.contact_methods (person_id);
create unique index contact_methods_unique_value_idx
on public.contact_methods (person_id, contact_type, contact_value);

create unique index contact_methods_one_preferred_per_person_idx
on public.contact_methods (person_id)
where is_preferred = true;

create index knows_about_person_id_idx on public.knows_about (person_id);
create index knows_about_status_idx on public.knows_about (status);
create index knows_about_search_idx on public.knows_about using gin (
  to_tsvector('simple', coalesce(topic, '') || ' ' || coalesce(context, ''))
);

create index looking_for_person_id_idx on public.looking_for (person_id);
create index looking_for_status_idx on public.looking_for (status);
create index looking_for_asked_at_idx on public.looking_for (asked_at desc);
create index looking_for_search_idx on public.looking_for using gin (
  to_tsvector('simple', coalesce(ask, '') || ' ' || coalesce(context, ''))
);

create index can_help_with_person_id_idx on public.can_help_with (person_id);
create index can_help_with_status_idx on public.can_help_with (status);
create index can_help_with_search_idx on public.can_help_with using gin (
  to_tsvector('simple', coalesce(help_area, '') || ' ' || coalesce(context, ''))
);

create index interactions_person_id_idx on public.interactions (person_id);
create index interactions_date_idx on public.interactions (interaction_date desc);
create index interactions_search_idx on public.interactions using gin (
  to_tsvector('simple', coalesce(summary, '') || ' ' || coalesce(raw_text, ''))
);

create index introductions_from_person_id_idx on public.introductions (from_person_id);
create index introductions_to_person_id_idx on public.introductions (to_person_id);
create index introductions_requested_by_person_id_idx on public.introductions (requested_by_person_id);
create index introductions_intro_date_idx on public.introductions (intro_date desc);
create index introductions_status_idx on public.introductions (status);

create index relationship_sources_person_id_idx on public.relationship_sources (person_id);
create index relationship_sources_date_idx on public.relationship_sources (source_date desc);
create index relationship_sources_type_idx on public.relationship_sources (source_type);

create index referrals_person_id_idx on public.referrals (person_id);
create index referrals_referrer_person_id_idx on public.referrals (referrer_person_id);
create index referrals_referred_at_idx on public.referrals (referred_at desc);

create or replace function public.search_people(search_query text)
returns table (
  id uuid,
  display_name text,
  first_name text,
  last_name text,
  location text,
  current_context text,
  notes text,
  last_interaction_at date,
  created_at timestamptz,
  updated_at timestamptz
)
language sql
stable
as $$
  select
    p.id,
    p.display_name,
    p.first_name,
    p.last_name,
    p.location,
    p.current_context,
    p.notes,
    p.last_interaction_at,
    p.created_at,
    p.updated_at
  from public.people p
  where
    nullif(btrim(search_query), '') is null
    or to_tsvector(
      'simple',
      concat_ws(' ', p.display_name, p.first_name, p.last_name, p.location, p.current_context, p.notes)
    ) @@ plainto_tsquery('simple', search_query)
    or exists (
      select 1
      from public.knows_about ka
      where ka.person_id = p.id
        and to_tsvector('simple', concat_ws(' ', ka.topic, ka.context))
          @@ plainto_tsquery('simple', search_query)
    )
    or exists (
      select 1
      from public.looking_for lf
      where lf.person_id = p.id
        and to_tsvector('simple', concat_ws(' ', lf.ask, lf.context))
          @@ plainto_tsquery('simple', search_query)
    )
    or exists (
      select 1
      from public.can_help_with chw
      where chw.person_id = p.id
        and to_tsvector('simple', concat_ws(' ', chw.help_area, chw.context))
          @@ plainto_tsquery('simple', search_query)
    )
    or exists (
      select 1
      from public.interactions i
      where i.person_id = p.id
        and to_tsvector('simple', concat_ws(' ', i.summary, i.raw_text))
          @@ plainto_tsquery('simple', search_query)
    )
  order by p.last_interaction_at desc nulls last, p.display_name asc;
$$;

-- MVP access note:
-- Row level security stays enabled, but this migration intentionally does not
-- add permissive policies. The FastAPI MVP uses server-side Supabase access
-- with SUPABASE_SERVICE_ROLE_KEY only. Never expose SUPABASE_SERVICE_ROLE_KEY
-- to browser code or client-side templates.
alter table public.people enable row level security;
alter table public.contact_methods enable row level security;
alter table public.knows_about enable row level security;
alter table public.looking_for enable row level security;
alter table public.can_help_with enable row level security;
alter table public.interactions enable row level security;
alter table public.introductions enable row level security;
alter table public.relationship_sources enable row level security;
alter table public.referrals enable row level security;
