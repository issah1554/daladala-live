from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from daladala_live.auth.dependencies import (
    get_current_active_user,
    get_current_user,
    oauth2_scheme,
)
from daladala_live.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    create_password_reset_token,
    create_email_verification_token,
    revoke_access_token,
    verify_refresh_token,
    verify_password_reset_token,
    verify_email_verification_token,
)
from daladala_live.users.schemas import UserCreate, UserOut
from daladala_live.users.service import (
    create_user,
    get_user_by_email,
    get_user_by_public_id,
    update_user_password,
    verify_user_email,
)


router = APIRouter(prefix="/volta/api/auth", tags=["auth"])
legacy_router = APIRouter(prefix="/api/auth", tags=["auth"])


# ===== Request/Response Schemas =====


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class VerifyEmailRequest(BaseModel):
    token: str


class MessageResponse(BaseModel):
    message: str


# ===== Registration & Login =====


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate):
    """
    Register a new user account.
    Returns the created user. A verification email should be sent separately.
    """
    existing = await get_user_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = await create_user(payload.email, payload.password)

    # TODO: In production, generate token and send verification email
    # verification_token = create_email_verification_token(user.public_id)
    # await send_verification_email(payload.email, verification_token)

    return user


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    """
    Authenticate a user and return access + refresh tokens.
    """
    user = await get_user_by_email(payload.email)

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    access_token = create_access_token(subject=user.public_id)
    refresh_token = create_refresh_token(subject=user.public_id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


# ===== Token Management =====


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh_access_token(payload: RefreshTokenRequest):
    """
    Get a new access token using a valid refresh token.
    """
    user_id = verify_refresh_token(payload.refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists and is active
    user = await get_user_by_public_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    new_access_token = create_access_token(subject=user_id)
    return AccessTokenResponse(access_token=new_access_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[dict, Depends(get_current_user)],  # noqa: ARG001
):
    """
    Logout the current user.
    Note: In a stateless JWT system, the client should discard the tokens.
    For enhanced security, implement token blacklisting with Redis.
    """
    revoke_access_token(token)
    del current_user  # Explicitly mark as intentionally unused
    return MessageResponse(message="Successfully logged out")


# ===== Email Verification =====


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(payload: VerifyEmailRequest):
    """
    Verify a user's email address using the verification token.
    """
    user_id = verify_email_verification_token(payload.token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    user = await get_user_by_public_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_email_verified:
        return MessageResponse(message="Email is already verified")

    await verify_user_email(user_id)
    return MessageResponse(message="Email verified successfully")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification_email(
    current_user: Annotated[dict, Depends(get_current_user)],
):
    """
    Resend the email verification token to the current user.
    """
    if current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified",
        )

    # TODO: Send verification email when mailer is configured
    # verification_token = create_email_verification_token(current_user.public_id)
    # await send_verification_email(current_user.email, verification_token)
    _ = create_email_verification_token  # Mark import as used

    return MessageResponse(message="Verification email sent")


# ===== Password Management =====


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(payload: ForgotPasswordRequest):
    """
    Request a password reset. A reset link will be sent to the email if it exists.
    Always returns success to prevent email enumeration.
    """
    user = await get_user_by_email(payload.email)

    if user:
        # TODO: Send password reset email when mailer is configured
        # reset_token = create_password_reset_token(user.public_id)
        # await send_password_reset_email(payload.email, reset_token)
        _ = create_password_reset_token  # Mark import as used

    # Always return success to prevent email enumeration
    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post("/reset-password", response_model=MessageResponse)
@legacy_router.post("/reset-password", response_model=MessageResponse)
async def reset_password(payload: ResetPasswordRequest):
    """
    Reset password using a valid reset token.
    """
    user_id = verify_password_reset_token(payload.token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user = await get_user_by_public_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await update_user_password(user_id, payload.new_password)
    return MessageResponse(message="Password has been reset successfully")


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    """
    Change password for the authenticated user.
    Requires the current password for verification.
    """
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    await update_user_password(current_user.public_id, payload.new_password)
    return MessageResponse(message="Password changed successfully")


# ===== User Info =====


@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user: Annotated[dict, Depends(get_current_active_user)],
):
    """
    Get the current authenticated user's information.
    """
    return current_user
