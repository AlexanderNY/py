from fastapi import APIRouter, HTTPException, status, Depends
from schemas import UserProfile, UserProfileUpdate
from services.auth_service import update_user_profile, get_all_users
from utils.exceptions import UserAlreadyExistsError, UserNotFoundError
from dependencies import get_current_user, get_admin_user
from typing import Dict, List


router = APIRouter(tags=["profile"])


@router.get("/profile", response_model=UserProfile)
async def get_profile(current_user: Dict = Depends(get_current_user)) -> UserProfile:
    """Получение профиля текущего пользователя."""
    return UserProfile(
        id=current_user.get("id"),
        username=current_user["username"],
        email=current_user["email"],
        role=current_user["role"],
        is_email_verified=current_user["is_email_verified"],
        created_at=current_user["created_at"]
    )


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict = Depends(get_current_user)
) -> UserProfile:
    """Обновление профиля текущего пользователя."""
    try:
        updated_user = await update_user_profile(
            user_id=current_user["id"],
            username=profile_update.username,
            email=profile_update.email
        )
        
        return UserProfile(
            id=updated_user.get("id"),
            username=updated_user["username"],
            email=updated_user["email"],
            role=updated_user["role"],
            is_email_verified=updated_user["is_email_verified"],
            created_at=updated_user["created_at"]
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/users", response_model=List[UserProfile])
async def get_users(admin_user: Dict = Depends(get_admin_user)) -> List[UserProfile]:
    """Получение списка всех пользователей (только для администраторов)."""
    try:
        users = await get_all_users()
        return [
            UserProfile(
                id=user.get("id"),
                username=user["username"],
                email=user["email"],
                role=user["role"],
                is_email_verified=user["is_email_verified"],
                created_at=user["created_at"]
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )

