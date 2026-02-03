from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from volta_api.core.security import verify_access_token
from volta_api.users.service import get_user_by_public_id


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Dependency to get the current authenticated user from the access token.
    Use this to protect routes that require authentication.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify the access token
    user_id = verify_access_token(token)
    if user_id is None:
        raise credentials_exception

    # Get user from database
    user = await get_user_by_public_id(user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """
    Dependency to get the current active user.
    Raises 403 if user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def get_current_verified_user(
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    """
    Dependency to get the current user with verified email.
    Raises 403 if email is not verified.
    """
    if not current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified",
        )
    return current_user
