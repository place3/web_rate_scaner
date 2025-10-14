import os.path
from fastapi import HTTPException

from fastapi import APIRouter

router = APIRouter(prefix="/manage", tags=["Manage"])

UPLOAD_DIR = "app/uploads"

@router.delete("/delete_all")
async def delete_all():
    if not os.path.exists(UPLOAD_DIR):
        raise HTTPException(status_code=404, detail="Папка для сканов не найдена")

    deleted_files = []

    # Проходим по всем файлам и удаляем их
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        try:
            os.remove(file_path)
            deleted_files.append(filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при удалении {filename}: {e}")

    return {"status": "ok", "deleted": deleted_files}