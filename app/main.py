from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .database import engine, Base
from .config import BASE_DIR
from .routes import auth, transactions

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

app.add_middleware(
    SessionMiddleware,
    secret_key="chave_super_secreta"
)

app.include_router(auth.router)
app.include_router(transactions.router)
