import os
import webbrowser
from typing import Optional, Dict, Any
from app.config import (
    FYERS_CLIENT_ID,
    FYERS_SECRET_KEY,
    FYERS_REDIRECT_URI,
)

try:
    from fyers_apiv3 import fyersModel
    HAS_FYERS_LIB = True
except ImportError:
    HAS_FYERS_LIB = False


class FyersAuth:
    """
    Handles Fyers API v3 OAuth login and access token generation.
    """
    def __init__(
        self,
        client_id: Optional[str] = None,
        secret_key: Optional[str] = None,
        redirect_uri: Optional[str] = None,
    ):
        self.client_id = client_id or FYERS_CLIENT_ID
        self.secret_key = secret_key or FYERS_SECRET_KEY
        self.redirect_uri = redirect_uri or FYERS_REDIRECT_URI
        self.session = None

    def generate_login_url(self) -> str:
        if not HAS_FYERS_LIB:
            raise RuntimeError("fyers_apiv3 library not installed.")

        self.session = fyersModel.SessionModel(
            client_id=self.client_id,
            secret_key=self.secret_key,
            redirect_uri=self.redirect_uri,
            response_type="code",
            grant_type="authorization_code",
            state="algoscreener"
        )
        return self.session.generate_authcode()

    def generate_access_token(self, auth_code: str) -> str:
        if not self.session:
            self.generate_login_url()

        self.session.set_token(auth_code)
        response = self.session.generate_token()

        if response.get("s") != "ok":
            raise Exception(f"Fyers Authentication failed: {response}")

        return response.get("access_token", "")
