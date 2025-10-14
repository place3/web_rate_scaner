from http.client import HTTPException
from itertools import chain

from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.openapi.utils import status_code_ranges
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
import uuid

router = APIRouter(prefix="/upload", tags=["Upload"])
templates = Jinja2Templates(directory="app/templates")


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Настройки
ALLOWED_EXT = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif"}
MAX_FILE_SIZE = 40 * 1920 * 1080  # 40 MB per file, поменяй при необходимости
MAX_TOTAL_FILES = 200  # защита от слишком большого количества файлов

def secure_filename(filename: str) -> str:
    # Очень простая санитаризация имени, при необходимости замени на werkzeug.utils.secure_filename
    return os.path.basename(filename).replace(" ", "_")

async def save_upload_file(upload_file: UploadFile, dest: Path, max_size: int):
    tmp_path = dest.with_suffix(dest.suffix + ".part")
    size = 0
    try:
        with tmp_path.open("wb") as buffer:
            while True:
                chunk = await upload_file.read(1024*1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_size:
                    raise HTTPException(status_code = 413, detail= f"file too large: {upload_file.filename}")
                buffer.write(chunk)
        tmp_path.rename(dest)
    finally:
        await upload_file.close()
        if tmp_path.exists() and not dest.exists():
            tmp_path.unlink(missing_ok=True)


@router.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@router.post("", response_class=JSONResponse)
async def upload(files: list[UploadFile] = File(...), session_id: str | None = Form(None)):
    """
    Принимает список файлов и optional session_id.
    Возвращает JSON:
    { "session_id": "...", "files": [{filename, saved, reason?}, ...] }
    """
    if not files:
        raise HTTPException(status_code=400, detail="no files uploaded")

    if len(files) > MAX_TOTAL_FILES:
        raise HTTPException(status_code=400, detail=f"too many files (limit {MAX_TOTAL_FILES})")

    if not session_id:
        session_id = str(uuid.uuid4())

    # session_dir = UPLOAD_DIR / session_id
    # session_dir.mkdir(parents=True, exist_ok=True)
    session_dir = UPLOAD_DIR
    session_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []
    for f in files:
        filename = secure_filename(f.filename or "")
        if not filename:
            saved_files.append({"filename": f.filename, "saved": False, "reason": "empty filename"})
            continue

        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXT:
            saved_files.append({"filename": filename, "saved": False, "reason": f"forbidden extension: {ext}"})
            # consume stream to avoid broken pipe on client side
            await f.read()
            continue

        # уникализируем имя, чтобы не перезаписать
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        dest = session_dir / unique_name

        try:
            await save_upload_file(f, dest, MAX_FILE_SIZE)
            saved_files.append({"filename": filename, "saved": True, "stored_as": unique_name})
        except HTTPException as he:
            saved_files.append({"filename": filename, "saved": False, "reason": he.detail})
        except Exception as e:
            saved_files.append({"filename": filename, "saved": False, "reason": str(e)})

    # сохраняем мета-инфо о сессии (список файлов) — полезно для последующего сканирования
    try:
        files_list = [r["stored_as"] for r in saved_files if r.get("saved")]
        (session_dir / "._files_list.txt").write_text("\n".join(files_list))
    except Exception:
        pass  # не критично

    return JSONResponse({"session_id": session_id, "files": saved_files})