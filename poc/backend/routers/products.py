from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.dependencies import get_current_user, get_product_service
from backend.models.user import User
from backend.schemas.chat import ChatHistoryItem, ChatRequest, ChatResponse
from backend.schemas.product import (
    ProductAnalysisResponse,
    ProductUrlRequest,
    RecommendSizeRequest,
    SizeRecommendationResponse,
    TryOnRequest,
    TryOnResponse,
)
from backend.services.product_service import ProductService

router = APIRouter(tags=["products"])


@router.post("/analyze-product", response_model=ProductAnalysisResponse)
async def analyze_product(
    data: ProductUrlRequest,
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
    db: Session = Depends(get_db),
) -> ProductAnalysisResponse:
    try:
        return await product_service.analyze_product(db, current_user, str(data.url))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/recommend-size", response_model=SizeRecommendationResponse)
def recommend_size(
    data: RecommendSizeRequest,
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
    db: Session = Depends(get_db),
) -> SizeRecommendationResponse:
    try:
        return product_service.recommend_size(db, current_user, data.product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/generate-tryon", response_model=TryOnResponse)
async def generate_tryon(
    data: TryOnRequest,
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
    db: Session = Depends(get_db),
) -> TryOnResponse:
    try:
        return await product_service.generate_tryon(db, current_user, data.product_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/chat", response_model=ChatResponse)
def chat(
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
    db: Session = Depends(get_db),
) -> ChatResponse:
    reply = product_service.chat(db, current_user, data.message, data.product_id)
    history = product_service.get_history(db, current_user)
    latest = history[0] if history else None
    return ChatResponse(reply=reply, message_id=latest.id if latest else 0)


@router.get("/history", response_model=list[ChatHistoryItem])
def history(
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
    db: Session = Depends(get_db),
) -> list[ChatHistoryItem]:
    messages = product_service.get_history(db, current_user)
    return [
        ChatHistoryItem(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            product_id=msg.product_id,
            created_at=msg.created_at.isoformat() if msg.created_at else "",
        )
        for msg in messages
    ]
