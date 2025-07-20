import random
import logging
from sqlalchemy.orm import Session
from typing import Optional
from services.common.models.user import User
from services.common.models.user_wallet import UserWallet
from services.common.models.user_access_token import UserAccessToken

from services.common.redis import redis_client
from services.common.redis_keys import RedisKeys
from services.common.database import SessionLocal
from services.common.utils.email_utils import EmailUtils
from services.common.utils.cache_utils import CacheUtils
from services.common.redis_keys import RedisKeys

from services.admin_service.repositories.user_repository import UserRepository
from services.admin_service.repositories.user_access_token_repository import UserAccessTokenRepository
from services.admin_service.services.sys_config_service import SysConfigService
from services.admin_service.constants.sys_config_key import (
    KEY_LOGIN_GOOGLE_CLIENT,
    KEY_LOGIN_GOOGLE_SECRET,
    KEY_LOGIN_GOOGLE_REDIRECT_URI,
    KEY_LOGIN_GOOGLE_ENABLE,
)

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token
import requests

logger = logging.getLogger(__name__)


class AuthService:

    def __init__(self, db: Session = SessionLocal()):
        self.db = db
        self.user_repository = UserRepository(db)
        self.user_access_token_repository = UserAccessTokenRepository(db)
        self.sys_config_service = SysConfigService(db)

    def send_email_login_captcha(self, email: str) -> bool:
        """
        Sends a login captcha code to the specified email address.
        The function generates a random 6-digit captcha code, stores it in Redis cache for 10 minutes,
        and sends the code to the user's email using HTML template.
        Args:
            email (str): The recipient's email address.
        Returns:
            bool: True if email was sent successfully, otherwise False.
        """
        # Generate random 6-digit verification code
        captcha = str(random.randint(100000, 999999))

        # Cache to redis
        CacheUtils.set_cache(RedisKeys.email_login_captcha(email), captcha, 10 * 60)

        # Send verification code using HTML email template
        return EmailUtils.send_register_code_email(self.db, email, captcha)

    def email_login(self, email: str, captcha: str) -> Optional[str]:
        cache_value = CacheUtils.get_cache(RedisKeys.email_login_captcha(email))
        if cache_value is None:
            logger.warning(f"not found captcha, email: {email}")
            return None
        if captcha == cache_value:
            logger.info(f"check email login code right, email: {email}")
            user = self.user_repository.get_by_email(email)

            # User doesn't exist, register first
            if user is None:
                user = self.user_repository.create(email=email, register_type="email", role_id=2)
            if user is None:
                logger.warning(f"Failed to register user with email: {email}")
                return None

            # Create user access token
            token = self.create_user_token(user.id)
            if token is None:
                logger.warning(f"Failed to create user token for email: {email}")
                return None
            # Clear verification code cache
            CacheUtils.set_cache(RedisKeys.email_login_captcha(email), None)
            return token
        return None

    def create_user_token(self, user_id: str) -> Optional[str]:
        user_access_token = self.user_access_token_repository.create(user_id)
        if user_access_token is None:
            logger.error(f"Failed to create user access token for user_id: {user_id}")
            return None
        # Cache user access token
        return user_access_token.token

    def account_login(self, account: str, password: str) -> Optional[str]:
        user = self.user_repository.get_by_account(account)
        if user and user.password == password:
            token = self.create_user_token(user.id)
            if token:
                return token
        return None

    def logout(self, token: str) -> bool:
        """
        Logs out the user by deleting their access token.
        Args:
            token (str): The user's access token.
        Returns:
            bool: True if logout was successful, False otherwise.
        """
        try:
            self.user_access_token_repository.delete_by_token(token)
            return True
        except Exception as e:
            logger.error(f"Failed to logout user with token {token}: {e}")
            return False

    def google_login(self, redirect_uri: str, code: str, state: str) -> Optional[str]:
        """
        Google OAuth login method.
        Args:
            code (str): Google OAuth authorization code
            state (str): OAuth state parameter for security
        Returns:
            Optional[str]: User token if login successful, None otherwise
        """
        try:
            # Get Google OAuth configuration from system config
            google_client_id = self.sys_config_service.get_value_by_key(KEY_LOGIN_GOOGLE_CLIENT)
            google_client_secret = self.sys_config_service.get_value_by_key(KEY_LOGIN_GOOGLE_SECRET)
            google_redirect_uri = redirect_uri

            if not google_client_id or not google_client_secret or not google_redirect_uri:
                logger.error("Google OAuth configuration is incomplete")
                return None

            # Exchange authorization code for access token
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                "client_id": google_client_id,
                "client_secret": google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": google_redirect_uri,
            }

            token_response = requests.post(token_url, data=token_data)
            if token_response.status_code != 200:
                logger.error(f"Failed to exchange code for token: {token_response.text}")
                return None

            token_json = token_response.json()
            id_token_str = token_json.get("id_token")

            if not id_token_str:
                logger.error("No id_token in Google OAuth response")
                return None

            # Verify and decode the ID token
            try:
                idinfo = id_token.verify_oauth2_token(id_token_str, GoogleRequest(), google_client_id)
            except ValueError as e:
                logger.error(f"Invalid Google ID token: {e}")
                return None

            # Extract user information
            email = idinfo.get("email")
            name = idinfo.get("name")
            google_id = idinfo.get("sub")

            if not email:
                logger.error("No email in Google user info")
                return None

            # Check if user already exists
            user = self.user_repository.get_by_email(email)

            # Create user if doesn't exist
            if user is None:
                user = self.user_repository.create_google_user(email=email, name=name or email.split("@")[0], google_id=google_id)

            if user is None:
                logger.error(f"Failed to create/get user with email: {email}")
                return None

            # Create user token
            token = self.create_user_token(user.id)
            if token is None:
                logger.error(f"Failed to create user token for email: {email}")
                return None

            logger.info(f"Google login successful for email: {email}")
            return token

        except Exception as e:
            logger.error(f"Google login failed: {e}")
            return None
