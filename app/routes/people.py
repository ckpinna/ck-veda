from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app import db


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    error = None
    people = []
    try:
        people = db.list_people()[:6]
    except Exception as exc:
        error = str(exc)
    return templates.TemplateResponse("home.html", {"request": request, "people": people, "error": error})


@router.get("/people", response_class=HTMLResponse)
async def people_list(request: Request):
    error = None
    people = []
    try:
        people = db.list_people()
    except Exception as exc:
        error = str(exc)
    return templates.TemplateResponse("people.html", {"request": request, "people": people, "error": error})


@router.get("/people/{person_id}", response_class=HTMLResponse)
async def person_detail(request: Request, person_id: str):
    error = None
    detail = None
    try:
        detail = db.get_person_detail(person_id)
    except Exception as exc:
        error = str(exc)

    if not detail and not error:
        error = "Person not found."

    return templates.TemplateResponse("person_detail.html", {"request": request, "detail": detail, "error": error})
