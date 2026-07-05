from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.dependencies import get_current_user, get_product_service
from backend.models.user import User
from backend.schemas.user import ProfileResponse, ProfileUpdate
from backend.services.auth_service import build_profile_response, update_profile
from backend.services.product_service import ProductService

router = APIRouter(tags=["profile"])


@router.get("/profile", response_model=ProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    user = product_service.get_user_with_relations(db, current_user.id)
    return build_profile_response(user)


@router.put("/profile", response_model=ProfileResponse)
def put_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    user = product_service.get_user_with_relations(db, current_user.id)
    updated = update_profile(db, user, data)
    refreshed = product_service.get_user_with_relations(db, updated.id)
    return build_profile_response(refreshed)


@router.post("/upload-images")
async def upload_images(
    front: UploadFile | None = File(None),
    side: UploadFile | None = File(None),
    back: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    product_service: ProductService = Depends(get_product_service),
    db: Session = Depends(get_db),
):
    saved = await product_service.save_images(db, current_user, front, side, back)
    return {
        "uploaded": [
            {"image_type": img.image_type, "file_path": img.file_path}
            for img in saved
        ]
    }
