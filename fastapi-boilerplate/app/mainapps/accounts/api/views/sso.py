# app/api/routes/auth.py (or update your existing users.py)
"""
SSO Authentication endpoints for Google, Microsoft, and LinkedIn
"""
from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app import crud
from app.mainapps.accounts.api import deps
from app.core.config import settings
from app.core.security import create_access_token
from app.core.sso import google_sso, microsoft_sso, linkedin_sso
from app.mainapps.accounts.serializers import UserPublic

router = APIRouter(prefix="/oauth", tags=["sso-auth"])


# ============ GOOGLE SSO ============

@router.get("/google/login")
async def google_login():
    """Initialize Google login and redirect to Google"""
    if google_sso is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google SSO is not configured",
        )
    async with google_sso:
        return await google_sso.get_login_redirect(
            params={"prompt": "consent", "access_type": "offline"}
        )


@router.get("/google/callback", response_model=UserPublic)
async def google_callback(request: Request, session: Session = Depends(deps.get_db)):
    """Handle Google OAuth callback"""
    if google_sso is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google SSO is not configured",
        )
    
    try:
        async with google_sso:
            user_info = await google_sso.verify_and_process(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to verify Google token: {str(e)}",
        )
    
    # Get or create user
    user = crud.get_or_create_sso_user(
        session=session,
        email=user_info.email,
        full_name=user_info.display_name,
        provider="google",
        provider_id=user_info.id,
    )
    
    # Create access token
    access_token = create_access_token(
        user.id, expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    # Redirect to frontend with token
    redirect_url = f"{settings.FRONTEND_HOST}/auth/callback?token={access_token}"
    return RedirectResponse(url=redirect_url)


# ============ MICROSOFT SSO ============

@router.get("/microsoft/login")
async def microsoft_login():
    """Initialize Microsoft login and redirect to Microsoft"""
    if microsoft_sso is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Microsoft SSO is not configured",
        )
    async with microsoft_sso:
        return await microsoft_sso.get_login_redirect()


@router.get("/microsoft/callback", response_model=UserPublic)
async def microsoft_callback(request: Request, session: Session = Depends(deps.get_db)):
    """Handle Microsoft OAuth callback"""
    if microsoft_sso is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Microsoft SSO is not configured",
        )
    
    try:
        async with microsoft_sso:
            user_info = await microsoft_sso.verify_and_process(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to verify Microsoft token: {str(e)}",
        )
    
    # Get or create user
    user = crud.get_or_create_sso_user(
        session=session,
        email=user_info.email,
        full_name=user_info.display_name,
        provider="microsoft",
        provider_id=user_info.id,
    )
    
    # Create access token
    access_token = create_access_token(
        user.id, expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    # Redirect to frontend with token
    redirect_url = f"{settings.FRONTEND_HOST}/auth/callback?token={access_token}"
    return RedirectResponse(url=redirect_url)


# ============ LINKEDIN SSO ============

@router.get("/linkedin/login")
async def linkedin_login():
    """Initialize LinkedIn login and redirect to LinkedIn"""
    if linkedin_sso is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LinkedIn SSO is not configured",
        )
    async with linkedin_sso:
        return await linkedin_sso.get_login_redirect()


@router.get("/linkedin/callback", response_model=UserPublic)
async def linkedin_callback(request: Request, session: Session = Depends(deps.get_db)):
    """Handle LinkedIn OAuth callback"""
    if linkedin_sso is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LinkedIn SSO is not configured",
        )
    
    try:
        async with linkedin_sso:
            user_info = await linkedin_sso.verify_and_process(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to verify LinkedIn token: {str(e)}",
        )
    
    # Get or create user
    user = crud.get_or_create_sso_user(
        session=session,
        email=user_info.email,
        full_name=user_info.display_name,
        provider="linkedin",
        provider_id=user_info.id,
    )
    
    # Create access token
    access_token = create_access_token(
        user.id, expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    # Redirect to frontend with token
    redirect_url = f"{settings.FRONTEND_HOST}/auth/callback?token={access_token}"
    return RedirectResponse(url=redirect_url)