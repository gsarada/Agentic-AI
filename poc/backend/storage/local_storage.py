import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from backend.config import get_settings
from backend.storage.base import StorageProvider


class LocalStorageProvider(StorageProvider):
    def __init__(self) -> None:
        settings = get_settings()
        self.upload_root = Path(settings.upload_dir)
        self.generated_root = Path(settings.generated_dir)
        self.upload_root.mkdir(parents=True, exist_ok=True)
        self.generated_root.mkdir(parents=True, exist_ok=True)

    async def save_user_image(self, user_id: int, image_type: str, file: UploadFile) -> str:
        user_dir = self.upload_root / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(file.filename or "image.jpg").suffix or ".jpg"
        dest = user_dir / f"{image_type}{suffix}"
        content = await file.read()
        dest.write_bytes(content)
        return str(dest.relative_to(self.upload_root.parent))

    async def save_generated_image(self, user_id: int, source_path: Path, suffix: str = ".jpg") -> str:
        user_dir = self.generated_root / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        dest = user_dir / f"{uuid4().hex}{suffix}"
        shutil.copy2(source_path, dest)
        return str(dest.relative_to(self.generated_root.parent))

    def get_absolute_path(self, relative_path: str) -> Path:
        settings = get_settings()
        base = Path(settings.upload_dir).parent
        return base / relative_path
