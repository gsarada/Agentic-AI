import json
from pathlib import Path

import httpx
from fastapi import UploadFile
from sqlalchemy.orm import Session, joinedload

from backend.agents.workflow import StylistWorkflow
from backend.models.chat import ChatMessage
from backend.models.product import GeneratedImage, Product, Recommendation
from backend.models.user import User, UserImage
from backend.providers.tryon import get_tryon_provider
from backend.schemas.product import (
    ProductAnalysisResponse,
    ProductKnowledgeProfile,
    SizeRecommendationResponse,
    TryOnResponse,
)
from backend.services.scraper_service import ProductScraperService
from backend.storage.local_storage import LocalStorageProvider
from backend.utils.llm import to_json


class ProductService:
    def __init__(self) -> None:
        self.scraper = ProductScraperService()
        self.workflow = StylistWorkflow()
        self.storage = LocalStorageProvider()

    async def analyze_product(self, db: Session, user: User, url: str) -> ProductAnalysisResponse:
        raw = await self.scraper.scrape(url)
        result = self.workflow.run_analysis(raw, user)

        product = Product(
            user_id=user.id,
            source_url=url,
            raw_data=to_json(raw.model_dump()),
            structured_data=to_json(result["product_profile"].model_dump()),
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        return ProductAnalysisResponse(
            product_id=product.id,
            raw=raw,
            product_profile=result["product_profile"],
            customer_profile=result["customer_profile"],
        )

    def recommend_size(self, db: Session, user: User, product_id: int) -> SizeRecommendationResponse:
        product = db.query(Product).filter(Product.id == product_id, Product.user_id == user.id).first()
        if not product:
            raise ValueError("Product not found")

        raw_data = json.loads(product.raw_data or "{}")
        structured = json.loads(product.structured_data or "{}")
        from backend.schemas.product import RawProductData

        raw = RawProductData(**raw_data)
        product_profile = ProductKnowledgeProfile(**structured)
        result = self.workflow.run_analysis(raw, user)

        recommendation = result["size_recommendation"]
        review = result["review_intelligence"]

        record = Recommendation(
            user_id=user.id,
            product_id=product.id,
            recommended_size=recommendation.recommended_size,
            confidence_score=recommendation.confidence_score,
            alternative_size=recommendation.alternative_size,
            explanation=recommendation.explanation,
            review_summary=review.personalized_summary,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return SizeRecommendationResponse(
            recommendation_id=record.id,
            recommendation=recommendation,
            review_intelligence=review,
        )

    async def generate_tryon(self, db: Session, user: User, product_id: int | None = None) -> TryOnResponse:
        front_image = (
            db.query(UserImage)
            .filter(UserImage.user_id == user.id, UserImage.image_type == "front")
            .first()
        )
        if not front_image:
            raise ValueError("Upload a front image before generating try-on")

        user_image_path = self.storage.get_absolute_path(front_image.file_path)
        product_image_path: Path | None = None

        if product_id:
            product = db.query(Product).filter(Product.id == product_id, Product.user_id == user.id).first()
            if product and product.structured_data:
                images = json.loads(product.structured_data).get("product_images", [])
                if images:
                    product_image_path = await self._download_temp_image(images[0])

        provider = get_tryon_provider()
        generated = await provider.generate(user_image_path, product_image_path)
        relative = await self.storage.save_generated_image(user.id, generated)

        record = GeneratedImage(
            user_id=user.id,
            product_id=product_id,
            file_path=relative,
            provider=get_tryon_provider().__class__.__name__,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return TryOnResponse(
            generated_image_id=record.id,
            file_path=relative,
            provider=record.provider,
        )

    async def _download_temp_image(self, url: str) -> Path:
        from backend.config import get_settings

        settings = get_settings()
        temp_dir = Path(settings.generated_dir) / "tmp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        dest = temp_dir / "product.jpg"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            dest.write_bytes(response.content)
        return dest

    async def save_images(
        self,
        db: Session,
        user: User,
        front: UploadFile | None,
        side: UploadFile | None,
        back: UploadFile | None,
    ) -> list[UserImage]:
        saved: list[UserImage] = []
        for image_type, file in [("front", front), ("side", side), ("back", back)]:
            if not file:
                continue
            path = await self.storage.save_user_image(user.id, image_type, file)
            existing = (
                db.query(UserImage)
                .filter(UserImage.user_id == user.id, UserImage.image_type == image_type)
                .first()
            )
            if existing:
                existing.file_path = path
                record = existing
            else:
                record = UserImage(user_id=user.id, image_type=image_type, file_path=path)
                db.add(record)
            saved.append(record)
        db.commit()
        for record in saved:
            db.refresh(record)
        return saved

    def chat(self, db: Session, user: User, message: str, product_id: int | None = None) -> str:
        from backend.schemas.product import ProductKnowledgeProfile, RawProductData

        product_profile = None
        customer_profile = self.workflow.customer_agent.run(user)
        review_intel = None

        if product_id:
            product = db.query(Product).filter(Product.id == product_id, Product.user_id == user.id).first()
            if product and product.structured_data:
                product_profile = ProductKnowledgeProfile(**json.loads(product.structured_data))
            if product and product.raw_data:
                raw = RawProductData(**json.loads(product.raw_data))
                review_intel = self.workflow.review_agent.run(raw, customer_profile)

        reply = self.workflow.chat(message, user, product_profile, customer_profile, review_intel)

        db.add(ChatMessage(user_id=user.id, product_id=product_id, role="user", content=message))
        db.add(ChatMessage(user_id=user.id, product_id=product_id, role="assistant", content=reply))
        db.commit()
        return reply

    def get_history(self, db: Session, user: User) -> list[ChatMessage]:
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.user_id == user.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(100)
            .all()
        )

    def get_user_with_relations(self, db: Session, user_id: int) -> User | None:
        return (
            db.query(User)
            .options(
                joinedload(User.measurements),
                joinedload(User.preferences),
                joinedload(User.images),
            )
            .filter(User.id == user_id)
            .first()
        )
