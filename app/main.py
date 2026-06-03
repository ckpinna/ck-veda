from fastapi import FastAPI

from app.config import get_settings
from app.routes import api, ingest, people, search


settings = get_settings()
app = FastAPI(title=settings.app_name)

app.include_router(ingest.router)
app.include_router(people.router)
app.include_router(search.router)
app.include_router(api.router)
