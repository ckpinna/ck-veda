Personal Relationship Manager MVP

Python/FastAPI app for manual relationship-note ingestion.

## Local Setup

1. Create a virtual environment and install dependencies:

   ```sh
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in:

   - `OPENAI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`

3. Review the migration SQL:

   ```text
   supabase/migrations/20260603000100_initial_relationship_manager.sql
   ```

4. After review, apply the migration with your preferred Supabase workflow.

5. Run the app:

   ```sh
   uvicorn app.main:app --reload
   ```

## Current Scope

- Manual text ingestion only
- OpenAI structured extraction
- Pydantic validation
- Editable review before saving
- Supabase-backed relationship memory
- Simple SQL search
