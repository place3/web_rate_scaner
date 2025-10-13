# from tkinter.font import names
#
# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from back.routers import manage, process, upload
# from pydantic import BaseModel
#
# class User(BaseModel):
#     name: str
#     age: int
#     is_russian: bool
#
# app = FastAPI()
#
# @app.get('/', description="ROOT PAGE")
# def get_root():
#     return {"Hello" : "World"}
#
#
#
# @app.get("/User",
#          description="User page",
#          response_model=User
#          )
# def get_handler():
#     return User(name = "Makar", age=19, is_russian=True)
#
#
# @app.post("/user",
#           response_model=User)
# def create_user(user: User):
#     return user
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from app.routers import upload, process, manage

app = FastAPI(title="Document Scanner WebApp", debug=True)

# Определяем базовую директорию проекта (где лежит main.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Настраиваем пути к static и templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Подключаем роутеры
app.include_router(upload.router)
app.include_router(process.router)
app.include_router(manage.router)

@app.get("/test")
def test():
    print("✅ test handler called")
    return {"status": "ok"}

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
