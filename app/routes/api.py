from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app import db
from app.extraction import extraction_from_json, extraction_to_json, extract_relationships


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/api/extract", response_class=HTMLResponse)
async def extract_api(request: Request, note: str = Form(...)):
    try:
        extraction, warnings = extract_relationships(note)
        return templates.TemplateResponse(
            "review.html",
            {
                "request": request,
                "note": note,
                "extraction": extraction,
                "extraction_json": extraction_to_json(extraction),
                "warnings": warnings,
                "error": None,
            },
        )
    except Exception as exc:
        return templates.TemplateResponse("error.html", {"request": request, "title": "Extraction Failed", "error": str(exc)}, status_code=500)


@router.post("/api/save-extraction", response_class=HTMLResponse)
async def save_extraction_api(request: Request, extraction_json: str = Form(...)):
    form = await request.form()
    try:
        extraction = extraction_from_json(extraction_json)
        for person in extraction.people:
            selected = form.get(f"selected_existing_person_id__{person.temp_id}")
            person.selected_existing_person_id = str(selected) if selected else None

        result = db.save_extraction(extraction)
        saved_people = result.get("saved_people", [])
        if len(saved_people) == 1:
            return RedirectResponse(f"/people/{saved_people[0]['id']}", status_code=303)
        return RedirectResponse("/people", status_code=303)
    except ValidationError as exc:
        return templates.TemplateResponse(
            "review.html",
            {
                "request": request,
                "note": "",
                "extraction": None,
                "extraction_json": extraction_json,
                "warnings": [],
                "error": exc.json(indent=2),
            },
            status_code=422,
        )
    except Exception as exc:
        return templates.TemplateResponse("error.html", {"request": request, "title": "Save Failed", "error": str(exc)}, status_code=500)
