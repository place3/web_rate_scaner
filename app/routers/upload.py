from fastapi import APIRouter, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(prefix="/upload", tags=["Upload"])
templates = Jinja2Templates(directory="app/templates")


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Настройки
ALLOWED_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif"}
MAX_FILE_SIZE = 40 * 1920 * 1080  # 40 MB per file, поменяй при необходимости
MAX_TOTAL_FILES = 200  # защита от слишком большого количества файлов

def secure_filename(filename: str) -> str:
    # Очень простая санитаризация имени, при необходимости замени на werkzeug.utils.secure_filename
    return os.path.basename(filename).replace(" ", "_")


@router.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@router.post("/files")
async def upload_files(files: list[UploadFile] = File(...)):
    """Приём и сохранение файлов"""
    saved_files = []
    for file in files:
        path = os.path.join(UPLOAD_DIR, file.filename)
        with open(path, "wb") as f:
            f.write(await file.read())
        saved_files.append(file.filename)
    return JSONResponse({"status": "ok", "files": saved_files})