from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
import time
import os

router = APIRouter(prefix="/process", tags=["Process"])
templates = Jinja2Templates(directory="app/templates")

RESULT_PATH = "results/result.xlsx"

@router.get("/", response_class=HTMLResponse)
async def process_page(request: Request):
    return templates.TemplateResponse("process.html", {"request": request})


@router.post("/start")
async def start_processing():
    """Здесь вызывается твой сканер"""
    time.sleep(2)  # имитация обработки
    # ТУТ ты вставишь вызов своей функции сканирования
    # например: scanner.process_all(input_dir="uploads", output_file=RESULT_PATH)
    open(RESULT_PATH, "w").write("test")  # временно создаём файл-заглушку
    return JSONResponse({"status": "done", "file": RESULT_PATH})


@router.get("/download")
async def download_result():
    """Скачивание Excel-файла"""
    if not os.path.exists(RESULT_PATH):
        return JSONResponse({"error": "no result yet"}, status_code=404)
    return FileResponse(RESULT_PATH, filename="result.xlsx")