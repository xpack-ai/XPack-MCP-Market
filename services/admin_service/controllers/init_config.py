# Read config from sys_config table, key is configured in services/admin_service/constants/sys_config_key.py

import logging
from fastapi import APIRouter, Depends
import json
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.admin_service.services.sys_config_service import SysConfigService
from services.admin_service.constants.sys_config_key import (
    KEY_PLATFORM_NAME,
    KEY_PLATFORM_LOGO,
    KEY_WEBSITE_TITLE,
    KEY_HEADLINE,
    KEY_SUBHEADLINE,
    KEY_LANGUAGE,
    KEY_THEME,
    KEY_ABOUT_PAGE,
    KEY_LOGIN_GOOGLE_CLIENT,
    KEY_LOGIN_GOOGLE_ENABLE,
    KEY_LOGIN_EMAIL_ENABLE,
    KEY_LOGIN_EMAIL_MODE,
    KEY_FAQ,
    KEY_EMBEDED_HTML,
    KEY_TOP_NAVIGATION,
    KEY_MCP_SERVER_PREFIX
)
from services.admin_service.services.payment_channel_service import PaymentChannelService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/config", summary="Get configuration (no login required)", tags=["common"])
def get_config(
        db: Session = Depends(get_db),
):
    """Get platform configuration settings without authentication."""
    try:
        # Create service instance
        sys_config_service = SysConfigService(db)
        payment_channel_service = PaymentChannelService(db)

        # Get platform config
        platform_name = sys_config_service.get_value_by_key(KEY_PLATFORM_NAME) or "XPack"
        platform_logo = sys_config_service.get_value_by_key(KEY_PLATFORM_LOGO) or ""
        website_title = sys_config_service.get_value_by_key(KEY_WEBSITE_TITLE) or ""
        headline = sys_config_service.get_value_by_key(KEY_HEADLINE) or ""
        subheadline = sys_config_service.get_value_by_key(KEY_SUBHEADLINE) or ""
        language = sys_config_service.get_value_by_key(KEY_LANGUAGE) or ""
        theme = sys_config_service.get_value_by_key(KEY_THEME) or ""
        about_page = sys_config_service.get_value_by_key(KEY_ABOUT_PAGE,True) or ""

        # Get login config
        google_client_id = sys_config_service.get_value_by_key(KEY_LOGIN_GOOGLE_CLIENT) or ""
        google_is_enabled_raw = sys_config_service.get_value_by_key(KEY_LOGIN_GOOGLE_ENABLE) or "false"
        # Convert to boolean
        google_is_enabled = google_is_enabled_raw.lower() in ("true", "t", "yes", "y", "1")
        
        # Get login email config
        email_is_enabled_raw = sys_config_service.get_value_by_key(KEY_LOGIN_EMAIL_ENABLE) or "false"
        # Convert to boolean
        email_is_enabled = email_is_enabled_raw.lower() in ("true", "t", "yes", "y", "1")
        email_mode = sys_config_service.get_value_by_key(KEY_LOGIN_EMAIL_MODE) or "password"
        mcp_server_prefix = sys_config_service.get_value_by_key(KEY_MCP_SERVER_PREFIX) or ""

        # Get homepage config
        faq = sys_config_service.get_value_by_key(KEY_FAQ) or "[]"
        embeded_html = sys_config_service.get_value_by_key(KEY_EMBEDED_HTML,True) or "{}"
        top_navigation = sys_config_service.get_value_by_key(KEY_TOP_NAVIGATION) or "[]"
        try:
            faq = json.loads(faq)
        except json.JSONDecodeError:
            return ResponseUtils.error("FAQ配置格式错误")
        try:
            embeded_html = json.loads(embeded_html)
        except json.JSONDecodeError:
            return ResponseUtils.error("Embeded HTML配置格式错误")
        try:
            top_navigation = json.loads(top_navigation)
        except json.JSONDecodeError:
            return ResponseUtils.error("Top Navigation配置格式错误")
        # Build response data
        config_data = {
            "login": {
                "google": {"client_id": google_client_id, "is_enabled": google_is_enabled},
                "email": {"is_enabled": email_is_enabled, "mode": email_mode},
            },
            "platform": {
                "name": platform_name,
                "logo": platform_logo,
                "website_title": website_title,
                "headline": headline,
                "subheadline": subheadline,
                "language": language,
                "theme": theme,
                "about_page": about_page,
                "mcp_server_prefix": mcp_server_prefix,
            },
            "faq": faq,
            "embeded_html": embeded_html,
            "top_navigation": top_navigation,
            "payment_channels": [{"id": item.id, "name": item.name} for item in payment_channel_service.available_list()],
        }

        return ResponseUtils.success(data=config_data)
    except Exception as e:
        logger.error(f"Failed to get config: {str(e)}")
        return ResponseUtils.error(message="Failed to get configuration")

@router.get("/homepage", summary="Get homepage configuration (no login required)", tags=["common"])
def get_homepage_config(db: Session = Depends(get_db)):
    """Get homepage configuration settings without authentication."""
    try:
        # Create service instance
        sys_config_service = SysConfigService(db)

        # Get homepage config
        faq = sys_config_service.get_value_by_key(KEY_FAQ) or "[]"
        embeded_html = sys_config_service.get_value_by_key(KEY_EMBEDED_HTML,True) or "{}"
        top_navigation = sys_config_service.get_value_by_key(KEY_TOP_NAVIGATION) or "[]"
        try:
            faq = json.loads(faq)
        except json.JSONDecodeError:
            return ResponseUtils.error("FAQ配置格式错误")
        try:
            embeded_html = json.loads(embeded_html)
        except json.JSONDecodeError:
            return ResponseUtils.error("Embeded HTML配置格式错误")
        try:
            top_navigation = json.loads(top_navigation)
        except json.JSONDecodeError:
            return ResponseUtils.error("Top Navigation配置格式错误")
        config_data = {
            "faq": faq,
            "embeded_html": embeded_html,
            "top_navigation": top_navigation,
        }
        return ResponseUtils.success(data=config_data)
    except Exception as e:
        logger.error(f"Failed to get homepage config: {str(e)}")
        return ResponseUtils.error(message="Failed to get configuration")