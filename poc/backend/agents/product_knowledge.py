import json

from backend.agents.base import BaseAgent
from backend.schemas.product import ProductKnowledgeProfile, RawProductData


class ProductKnowledgeAgent(BaseAgent):
    name = "product_knowledge"

    def run(self, raw: RawProductData) -> ProductKnowledgeProfile:
        fallback = ProductKnowledgeProfile(
            name=raw.name,
            brand=raw.brand,
            fabric=raw.material,
            stretch="Unknown",
            fit=raw.fit,
            season="All-season",
            care_instructions="Follow garment label",
            available_sizes=raw.available_sizes,
            size_chart=raw.size_chart,
            review_summary="; ".join(raw.reviews[:3]),
            product_images=raw.product_images,
            price=raw.price,
            description=raw.description,
        )

        return self.llm.structured_completion(
            system_prompt=(
                "You are a fashion product analyst. Convert scraped product data into structured JSON. "
                "Infer fabric, stretch, season, and care instructions when possible."
            ),
            user_prompt=json.dumps(raw.model_dump(), indent=2),
            output_model=ProductKnowledgeProfile,
            fallback=fallback,
        )
