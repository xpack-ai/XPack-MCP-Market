from fastapi import APIRouter, Depends, Request, Body
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.admin_service.services.auth_service import AuthService
from services.admin_service.services.sys_config_service import SysConfigService
from services.admin_service.utils.user_utils import UserUtils
from services.admin_service.constants import sys_config_key

router = APIRouter()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

def get_sys_config_service(db: Session = Depends(get_db)) -> SysConfigService:
    return SysConfigService(db)


@router.post("/email/sign", response_model=dict)
def email_login(
    body: dict = Body(...), 
    auth_service: AuthService = Depends(get_auth_service), 
    sys_config_service: SysConfigService = Depends(get_sys_config_service),
    ):
    """Authenticate user via email and captcha code."""
    email_is_enabled_raw = sys_config_service.get_value_by_key(sys_config_key.KEY_LOGIN_EMAIL_ENABLE) or "false"
    # Convert to boolean
    email_is_enabled = email_is_enabled_raw.lower() in ("true", "t", "yes", "y", "1")
    if not email_is_enabled:
        return ResponseUtils.error(message="email login not enabled", code=400)
    email_mode = sys_config_service.get_value_by_key(sys_config_key.KEY_LOGIN_EMAIL_MODE) or "password"
    email = body.get("user_email")
    token = None
    match email_mode:
        case "password":
            password = body.get("password")
            if not email or not password:
                return ResponseUtils.error(message="email and password required", code=400)
            token = auth_service.email_login_by_password(email=email, password=password)
        case "captcha":
            captcha = body.get("captcha")
            if not email or not captcha:
                return ResponseUtils.error(message="email and captcha required", code=400)
            token = auth_service.email_login_by_captcha(email=email, captcha=captcha)
    if token:
        return ResponseUtils.success({"user_token": token})
    else:
        return ResponseUtils.error(message="login failed", code=401)


@router.post("/email/send_captcha", response_model=dict)
def email_login_send_captcha(body: dict = Body(...), auth_service: AuthService = Depends(get_auth_service)):
    """Send authentication captcha code to user's email."""
    email = body.get("user_email")
    if not email:
        return ResponseUtils.error(message="email required", code=400)
    if auth_service.send_email_login_captcha(email):
        return ResponseUtils.success()
    else:
        return ResponseUtils.error(message="send email fail")


@router.post("/account/sign", response_model=dict)
def account_login(body: dict = Body(...), auth_service: AuthService = Depends(get_auth_service)):
    """Authenticate user via username and password."""
    name = body.get("name")
    password = body.get("password")
    if not name or not password:
        return ResponseUtils.error(message="account and password required", code=400)
    token = auth_service.account_login(name, password)
    if token:
        return ResponseUtils.success({"user_token": token})
    else:
        return ResponseUtils.error(message="login failed", code=401)


@router.post("/google/sign", response_model=dict)
def google_login(request: Request, body: dict = Body(...), auth_service: AuthService = Depends(get_auth_service)):
    """Authenticate user via Google OAuth2 authorization code."""
    code = body.get("code")
    state = body.get("state")
    redirect_uri = body.get("redirect_uri")
    if not redirect_uri:
        return ResponseUtils.error(message="redirect_uri not found", code=400)
    if not code or not state:
        return ResponseUtils.error(message="code and state required", code=400)
    token = auth_service.google_login(redirect_uri, code, state)
    if token:
        return ResponseUtils.success({"user_token": token})
    else:
        return ResponseUtils.error(message=f"login failed: {redirect_uri}", code=401)


@router.delete("/logout", response_model=dict)
def logout(request: Request, auth_service: AuthService = Depends(get_auth_service)):
    """Log out current authenticated user."""
    user_token = UserUtils.get_request_user_token(request)
    auth_service.logout(user_token)
    return ResponseUtils.success(message="Logout successful")
