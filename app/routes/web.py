from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import get_user_by_email, hash_password, verify_password
from app.database import get_db
from app.models import Document, User
from app.services.pdf_service import build_pdf_from_text, extract_text_from_pdf
from app.services.s3_service import StorageService
from app.services.translation_service import translate_document

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def current_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


@router.get("/")
def home(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": ""})


@router.post("/register")
def register(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    full_name = full_name.strip()
    email = email.strip().lower()
    if len(full_name) < 2 or len(password) < 6:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Invalid name or password length."},
        )

    if get_user_by_email(db, email):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already exists."},
        )

    user = User(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard", status_code=302)


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": ""})


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Invalid email or password."}
        )

    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard", status_code=302)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    documents = (
        db.query(Document)
        .filter(Document.user_id == user.id)
        .order_by(Document.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "documents": documents, "error": "", "success": ""},
    )


@router.post("/translate")
async def translate_pdf(
    request: Request,
    source_language: str = Form("auto"),
    pdf_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    if not pdf_file.filename.lower().endswith(".pdf"):
        documents = (
            db.query(Document)
            .filter(Document.user_id == user.id)
            .order_by(Document.created_at.desc())
            .all()
        )
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "user": user,
                "documents": documents,
                "error": "Please upload a PDF file only.",
                "success": "",
            },
        )

    content = await pdf_file.read()
    storage = StorageService()

    document = Document(
        user_id=user.id,
        original_filename=pdf_file.filename,
        source_language=source_language.strip() or "auto",
        status="processing",
        original_s3_key=storage.upload_bytes(content, "originals", pdf_file.filename),
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        extracted_text = extract_text_from_pdf(content)
        if not extracted_text.strip():
            raise ValueError("No extractable text found in PDF.")

        translated_text = translate_document(extracted_text, document.source_language)
        translated_pdf = build_pdf_from_text(translated_text)
        translated_name = (
            pdf_file.filename.rsplit(".", 1)[0] + "_translated_english.pdf"
        )
        translated_key = storage.upload_bytes(
            translated_pdf, "translated", translated_name
        )

        document.translated_filename = translated_name
        document.translated_s3_key = translated_key
        document.status = "completed"
        db.commit()
    except Exception as ex:
        document.status = "failed"
        document.error_message = str(ex)
        db.commit()

    return RedirectResponse("/dashboard", status_code=302)


@router.get("/download/{document_id}")
def download(document_id: int, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", status_code=302)

    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == user.id)
        .first()
    )
    if not document or not document.translated_s3_key:
        raise HTTPException(status_code=404, detail="Translated file not found.")

    storage = StorageService()
    translated_bytes = storage.read_bytes(document.translated_s3_key)
    return StreamingResponse(
        BytesIO(translated_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{document.translated_filename}"'
        },
    )
