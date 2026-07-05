from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from backend.agents.conversation import ConversationAgent
from backend.agents.customer_profile import CustomerProfileAgent
from backend.agents.product_knowledge import ProductKnowledgeAgent
from backend.agents.review_intelligence import ReviewIntelligenceAgent
from backend.agents.size_recommendation import SizeRecommendationAgent
from backend.models.user import User
from backend.schemas.product import (
    CustomerAIProfile,
    ProductKnowledgeProfile,
    RawProductData,
    ReviewIntelligence,
    SizeRecommendation,
)
from backend.utils.logging import get_logger, log_duration

logger = get_logger(__name__)


class WorkflowState(TypedDict, total=False):
    raw_product: RawProductData
    user: User
    product_profile: ProductKnowledgeProfile
    customer_profile: CustomerAIProfile
    size_recommendation: SizeRecommendation
    review_intelligence: ReviewIntelligence
    error: str


class StylistWorkflow:
    def __init__(self) -> None:
        self.product_agent = ProductKnowledgeAgent()
        self.customer_agent = CustomerProfileAgent()
        self.size_agent = SizeRecommendationAgent()
        self.review_agent = ReviewIntelligenceAgent()
        self.conversation_agent = ConversationAgent()
        self.graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(WorkflowState)
        graph.add_node("product_knowledge", self._product_knowledge_node)
        graph.add_node("customer_profile", self._customer_profile_node)
        graph.add_node("review_intelligence", self._review_intelligence_node)
        graph.add_node("size_recommendation", self._size_recommendation_node)
        graph.set_entry_point("product_knowledge")
        graph.add_edge("product_knowledge", "customer_profile")
        graph.add_edge("customer_profile", "review_intelligence")
        graph.add_edge("review_intelligence", "size_recommendation")
        graph.add_edge("size_recommendation", END)
        return graph.compile()

    def _product_knowledge_node(self, state: WorkflowState) -> dict[str, Any]:
        with log_duration(logger, "agent_product_knowledge"):
            profile = self.product_agent.run(state["raw_product"])
            return {"product_profile": profile}

    def _customer_profile_node(self, state: WorkflowState) -> dict[str, Any]:
        with log_duration(logger, "agent_customer_profile"):
            profile = self.customer_agent.run(state["user"])
            return {"customer_profile": profile}

    def _review_intelligence_node(self, state: WorkflowState) -> dict[str, Any]:
        with log_duration(logger, "agent_review_intelligence"):
            review = self.review_agent.run(
                state["raw_product"],
                state["customer_profile"],
            )
            return {"review_intelligence": review}

    def _size_recommendation_node(self, state: WorkflowState) -> dict[str, Any]:
        with log_duration(logger, "agent_size_recommendation"):
            recommendation = self.size_agent.run(
                state["customer_profile"],
                state["product_profile"],
                state["raw_product"],
                state.get("review_intelligence"),
            )
            return {"size_recommendation": recommendation}

    def run_analysis(self, raw_product: RawProductData, user: User) -> WorkflowState:
        initial: WorkflowState = {"raw_product": raw_product, "user": user}
        return self.graph.invoke(initial)

    def chat(
        self,
        message: str,
        user: User,
        product_profile: ProductKnowledgeProfile | None = None,
        customer_profile: CustomerAIProfile | None = None,
        review_intelligence: ReviewIntelligence | None = None,
    ) -> str:
        return self.conversation_agent.run(
            message,
            user,
            product_profile,
            customer_profile,
            review_intelligence,
        )
