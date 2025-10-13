from fastapi import APIRouter

router = APIRouter(prefix="/manage", tags=["Manage"])

@router.delete("/delete_all")
async def delete_all():
    # Пока просто возвращаем ответ (позже добавим удаление)
    return {"status": "all files deleted"}