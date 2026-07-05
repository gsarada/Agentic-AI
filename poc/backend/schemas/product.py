from pydantic import BaseModel, Field, HttpUrl


class ProductUrlRequest(BaseModel):
    url: HttpUrl


class RawProductData(BaseModel):
    name: str = ""
    brand: str = ""
    price: str = ""
    available_sizes: list[str] = Field(default_factory=list)
    product_images: list[str] = Field(default_factory=list)
    description: str = ""
    material: str = ""
    fit: str = ""
    size_chart: dict = Field(default_factory=dict)
    reviews: list[str] = Field(default_factory=list)
    ratings: str = ""
    source_url: str = ""


class ProductKnowledgeProfile(BaseModel):
    name: str = ""
    brand: str = ""
    fabric: str = ""
    stretch: str = ""
    fit: str = ""
    season: str = ""
    care_instructions: str = ""
    available_sizes: list[str] = Field(default_factory=list)
    size_chart: dict = Field(default_factory=dict)
    review_summary: str = ""
    product_images: list[str] = Field(default_factory=list)
    price: str = ""
    description: str = ""


class CustomerAIProfile(BaseModel):
    body_shape: str = ""
    height: float | None = None
    waist: float | None = None
    chest: float | None = None
    preferred_fit: str = ""
    favorite_colors: list[str] = Field(default_factory=list)
    fabric_preference: list[str] = Field(default_factory=list)
    weight: float | None = None
    hip: float | None = None


class SizeRecommendation(BaseModel):
    recommended_size: str
    confidence_score: float
    explanation: str
    alternative_size: str | None = None


class ReviewIntelligence(BaseModel):
    pros: list[str] = Field(default_factory=list)
    cons: list[str] = Field(default_factory=list)
    sizing_feedback: str = ""
    fabric_feedback: str = ""
    quality: str = ""
    shrinkage: str = ""
    color_accuracy: str = ""
    durability: str = ""
    personalized_summary: str = ""


class ProductAnalysisResponse(BaseModel):
    product_id: int
    raw: RawProductData
    product_profile: ProductKnowledgeProfile
    customer_profile: CustomerAIProfile


class SizeRecommendationResponse(BaseModel):
    recommendation_id: int
    recommendation: SizeRecommendation
    review_intelligence: ReviewIntelligence


class TryOnResponse(BaseModel):
    generated_image_id: int
    file_path: str
    provider: str


class RecommendSizeRequest(BaseModel):
    product_id: int


class TryOnRequest(BaseModel):
    product_id: int | None = None
