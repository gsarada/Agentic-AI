import json

from backend.agents.base import BaseAgent
from backend.models.user import User
from backend.schemas.product import (
    CustomerAIProfile,
    ProductKnowledgeProfile,
    ReviewIntelligence,
    SizeRecommendation,
)


class SizeRecommendationAgent(BaseAgent):
    name = "size_recommendation"

    def run(
        self,
        customer: CustomerAIProfile,
        product: ProductKnowledgeProfile,
        raw_product,
        review: ReviewIntelligence | None = None,
    ) -> SizeRecommendation:
        sizes = product.available_sizes or ["S", "M", "L", "XL"]
        fallback_size = sizes[min(len(sizes) // 2, len(sizes) - 1)] if sizes else "M"
        fallback = SizeRecommendation(
            recommended_size=fallback_size,
            confidence_score=0.55,
            explanation=(
                f"Based on your {customer.body_shape or 'body'} shape and preferred "
                f"{customer.preferred_fit or 'regular'} fit, {fallback_size} is a reasonable starting point."
            ),
            alternative_size=sizes[-1] if len(sizes) > 1 else None,
        )

        context = {
            "customer_profile": customer.model_dump(),
            "product_profile": product.model_dump(),
            "size_chart": product.size_chart,
            "reviews": raw_product.reviews[:10],
            "review_intelligence": review.model_dump() if review else {},
        }

        return self.llm.structured_completion(
            system_prompt=(
                "You are an expert fit consultant. Recommend the best size with confidence score 0-1, "
                "explain WHY using measurements, size chart, and review sizing feedback. "
                "Provide an alternative size if the recommended size may be unavailable."
            ),
            user_prompt=json.dumps(context, indent=2),
            output_model=SizeRecommendation,
            fallback=fallback,
        )
