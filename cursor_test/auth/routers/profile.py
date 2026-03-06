from fastapi import APIRouter, HTTPException, status, Depends
from schemas import UserProfile, UserProfileUpdate, AdminUserUpdate, RoleTariffHistoryEntry
from services.auth_service import (
    update_user_profile,
    get_all_users,
    update_user_role_tariff,
    get_user_role_tariff_history,
)
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
        tariff=current_user.get("tariff", "free"),
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
            tariff=updated_user.get("tariff", "free"),
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
                tariff=user.get("tariff", "free"),
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


@router.patch("/users/{user_id}", response_model=UserProfile)
async def update_user_role_and_tariff(
    user_id: int,
    body: AdminUserUpdate,
    admin_user: Dict = Depends(get_admin_user)
) -> UserProfile:
    """Изменение роли и/или тарифа пользователя (только для администраторов)."""
    try:
        updated_user = await update_user_role_tariff(
            user_id=user_id,
            role=body.role,
            tariff=body.tariff,
            changed_by_user_id=admin_user.get("id"),
        )
        return UserProfile(
            id=updated_user.get("id"),
            username=updated_user["username"],
            email=updated_user["email"],
            role=updated_user["role"],
            tariff=updated_user.get("tariff", "free"),
            is_email_verified=updated_user["is_email_verified"],
            created_at=updated_user["created_at"]
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/users/{user_id}/role-tariff-history", response_model=List[RoleTariffHistoryEntry])
async def get_role_tariff_history(
    user_id: int,
    current_user: Dict = Depends(get_current_user),
) -> List[RoleTariffHistoryEntry]:
    """История изменений роли и тарифа. Админ — для любого user_id, иначе только свой."""
    is_admin = current_user.get("role") == "admin"
    if not is_admin and current_user.get("id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only view your own history.",
        )
    entries = await get_user_role_tariff_history(user_id)
    return [
        RoleTariffHistoryEntry(
            id=e["id"],
            user_id=e["user_id"],
            changed_at=e["changed_at"],
            changed_by_user_id=e.get("changed_by_user_id"),
            role_old=e.get("role_old"),
            role_new=e.get("role_new"),
            tariff_old=e.get("tariff_old"),
            tariff_new=e.get("tariff_new"),
        )
        for e in entries
    ]

