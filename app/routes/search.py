from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app import db


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str | None = None):
    error = None
    people = []
    if q and q.strip():
        try:
            people = db.list_people(q)
        except Exception as exc:
            error = str(exc)
    return templates.TemplateResponse("search.html", {"request": request, "q": q or "", "people": people, "error": error})
