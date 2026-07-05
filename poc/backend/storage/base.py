from abc import ABC, abstractmethod
from pathlib import Path

from fastapi import UploadFile


class StorageProvider(ABC):
    @abstractmethod
    async def save_user_image(self, user_id: int, image_type: str, file: UploadFile) -> str:
        pass

    @abstractmethod
    async def save_generated_image(self, user_id: int, source_path: Path, suffix: str = ".jpg") -> str:
        pass

    @abstractmethod
    def get_absolute_path(self, relative_path: str) -> Path:
        pass
