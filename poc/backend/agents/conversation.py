import json

from backend.agents.base import BaseAgent
from backend.models.user import User
from backend.schemas.product import CustomerAIProfile, ProductKnowledgeProfile, ReviewIntelligence


class ConversationAgent(BaseAgent):
    name = "conversation"

    def run(
        self,
        message: str,
        user: User,
        product_profile: ProductKnowledgeProfile | None = None,
        customer_profile: CustomerAIProfile | None = None,
        review_intelligence: ReviewIntelligence | None = None,
    ) -> str:
        context = {
            "user": {"name": user.name},
            "product_profile": product_profile.model_dump() if product_profile else {},
            "customer_profile": customer_profile.model_dump() if customer_profile else {},
            "review_intelligence": review_intelligence.model_dump() if review_intelligence else {},
        }

        return self.llm.text_completion(
            system_prompt=(
                "You are a helpful AI personal stylist. Answer fit, fabric, weather suitability, "
                "shrinkage, and color questions using the provided product and customer context. "
                "Be concise, practical, and personalized."
            ),
            user_prompt=f"Context:\n{json.dumps(context, indent=2)}\n\nUser question: {message}",
            fallback=(
                "I can help with fit and styling once product analysis is complete. "
                "Please analyze a product URL first."
            ),
        )
