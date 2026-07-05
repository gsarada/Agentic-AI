import json

from backend.agents.base import BaseAgent
from backend.models.user import User
from backend.schemas.product import CustomerAIProfile
from backend.utils.llm import deserialize_list


class CustomerProfileAgent(BaseAgent):
    name = "customer_profile"

    def run(self, user: User) -> CustomerAIProfile:
        m = user.measurements
        p = user.preferences
        fallback = CustomerAIProfile(
            body_shape=self._infer_body_shape(m.chest if m else None, m.waist if m else None, m.hip if m else None),
            height=m.height if m else None,
            waist=m.waist if m else None,
            chest=m.chest if m else None,
            preferred_fit=p.preferred_fit if p else "",
            favorite_colors=deserialize_list(p.preferred_colors if p else None),
            fabric_preference=deserialize_list(p.preferred_fabrics if p else None),
            weight=m.weight if m else None,
            hip=m.hip if m else None,
        )

        payload = {
            "name": user.name,
            "measurements": fallback.model_dump(),
            "preferences": {
                "preferred_fit": p.preferred_fit if p else None,
                "preferred_colors": deserialize_list(p.preferred_colors if p else None),
                "preferred_fabrics": deserialize_list(p.preferred_fabrics if p else None),
            },
        }

        return self.llm.structured_completion(
            system_prompt=(
                "You convert shopper profile data into a concise AI styling profile. "
                "Infer body shape from measurements when possible."
            ),
            user_prompt=json.dumps(payload, indent=2),
            output_model=CustomerAIProfile,
            fallback=fallback,
        )

    def _infer_body_shape(self, chest: float | None, waist: float | None, hip: float | None) -> str:
        if not chest or not waist:
            return "Average"
        if chest - waist > 12:
            return "Athletic"
        if hip and hip - waist > 10:
            return "Pear"
        if chest and waist and abs(chest - waist) < 5:
            return "Rectangle"
        return "Average"
