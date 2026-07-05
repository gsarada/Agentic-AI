from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import get_settings
from backend.database.connection import init_db
from backend.routers import auth, products, profile
from backend.utils.logging import configure_logging, get_logger

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(settings.debug)
    init_db()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.generated_dir).mkdir(parents=True, exist_ok=True)
    logger.info("application_started", app=settings.app_name)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(products.router)

images_root = Path(settings.upload_dir).parent
app.mount("/images", StaticFiles(directory=str(images_root)), name="images")


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}
