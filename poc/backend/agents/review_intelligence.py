import json

from backend.agents.base import BaseAgent
from backend.models.user import User
from backend.schemas.product import CustomerAIProfile, RawProductData, ReviewIntelligence


class ReviewIntelligenceAgent(BaseAgent):
    name = "review_intelligence"

    def run(self, raw: RawProductData, customer: CustomerAIProfile) -> ReviewIntelligence:
        fallback = ReviewIntelligence(
            pros=["Comfortable for daily wear"] if raw.reviews else [],
            cons=["Limited review data available"] if not raw.reviews else [],
            sizing_feedback="Check size chart before ordering.",
            fabric_feedback=raw.material or "Fabric details unavailable.",
            quality="Average based on limited data.",
            shrinkage="Unknown",
            color_accuracy="Unknown",
            durability="Unknown",
            personalized_summary=(
                f"With your preferred {customer.preferred_fit or 'regular'} fit, "
                f"compare your measurements against the size chart."
            ),
        )

        context = {
            "reviews": raw.reviews,
            "ratings": raw.ratings,
            "customer_profile": customer.model_dump(),
        }

        return self.llm.structured_completion(
            system_prompt=(
                "Summarize customer reviews into pros, cons, sizing, fabric, quality, shrinkage, "
                "color accuracy, and durability. Then personalize the summary for the shopper."
            ),
            user_prompt=json.dumps(context, indent=2),
            output_model=ReviewIntelligence,
            fallback=fallback,
        )
