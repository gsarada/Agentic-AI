from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw, ImageFont

from backend.config import Settings, get_settings
from backend.utils.logging import get_logger

logger = get_logger(__name__)


class VirtualTryOnProvider(ABC):
    @abstractmethod
    async def generate(self, user_image_path: Path, product_image_path: Path | None = None) -> Path:
        pass


class MockTryOnProvider(VirtualTryOnProvider):
    async def generate(self, user_image_path: Path, product_image_path: Path | None = None) -> Path:
        settings = get_settings()
        output_dir = Path(settings.generated_dir) / "tmp"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"mock_{uuid4().hex}.jpg"

        if user_image_path.exists():
            image = Image.open(user_image_path).convert("RGB")
        else:
            image = Image.new("RGB", (512, 768), color=(240, 240, 240))

        draw = ImageDraw.Draw(image)
        text = "Virtual Try-On Preview (Mock Provider)"
        draw.rectangle([(0, image.height - 80), (image.width, image.height)], fill=(30, 30, 30))
        draw.text((20, image.height - 55), text, fill=(255, 255, 255))
        image.save(output_path, format="JPEG", quality=90)
        logger.info("mock_tryon_generated", output=str(output_path))
        return output_path


class IDMVTONTryOnProvider(VirtualTryOnProvider):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def generate(self, user_image_path: Path, product_image_path: Path | None = None) -> Path:
        if not self.settings.idm_vton_api_url:
            logger.warning("idm_vton_not_configured_falling_back_to_mock")
            return await MockTryOnProvider().generate(user_image_path, product_image_path)

        import httpx

        settings = self.settings
        output_dir = Path(settings.generated_dir) / "tmp"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"idm_{uuid4().hex}.jpg"

        files = {"person_image": user_image_path.open("rb")}
        if product_image_path and product_image_path.exists():
            files["garment_image"] = product_image_path.open("rb")

        headers = {}
        if settings.idm_vton_api_key:
            headers["Authorization"] = f"Bearer {settings.idm_vton_api_key}"

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(settings.idm_vton_api_url, files=files, headers=headers)
            response.raise_for_status()
            output_path.write_bytes(response.content)

        logger.info("idm_vton_generated", output=str(output_path))
        return output_path


def get_tryon_provider(settings: Settings | None = None) -> VirtualTryOnProvider:
    settings = settings or get_settings()
    provider = settings.tryon_provider.lower()
    if provider == "idm-vton":
        return IDMVTONTryOnProvider(settings)
    return MockTryOnProvider()
