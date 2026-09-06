import os
from typing import Optional, Dict, Any
from app.config import (
    ANGELONE_API_KEY,
    ANGELONE_CLIENT_CODE,
    ANGELONE_PIN,
    ANGELONE_TOTP_SECRET,
)

try:
    import pyotp
    from SmartApi import SmartConnect
    HAS_SMARTAPI = True
except ImportError:
    HAS_SMARTAPI = False


class AngelOneAuth:
    """
    Handles AngelOne SmartConnect login, TOTP generation, and session management.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        client_code: Optional[str] = None,
        pin: Optional[str] = None,
        totp_secret: Optional[str] = None,
    ):
        self.api_key = api_key or ANGELONE_API_KEY
        self.client_code = client_code or ANGELONE_CLIENT_CODE
        self.pin = pin or ANGELONE_PIN
        self.totp_secret = totp_secret or ANGELONE_TOTP_SECRET
        self.smart_api = None
        self.session_data = None

    def generate_totp(self) -> str:
        if not self.totp_secret:
            raise ValueError("TOTP Secret not provided")
        return pyotp.TOTP(self.totp_secret).now()

    def login(self) -> Dict[str, Any]:
        if not HAS_SMARTAPI:
            raise RuntimeError("SmartApi library (smartapi-python) is not installed.")

        if not self.api_key or not self.client_code or not self.pin or not self.totp_secret:
            raise ValueError("Missing AngelOne API key, Client Code, PIN, or TOTP secret.")

        self.smart_api = SmartConnect(api_key=self.api_key)
        totp = self.generate_totp()

        session = self.smart_api.generateSession(
            self.client_code,
            self.pin,
            totp
        )
        self.session_data = session
        return session

    def get_jwt_token(self) -> Optional[str]:
        if self.session_data and self.session_data.get("status"):
            return self.session_data.get("data", {}).get("jwtToken")
        return None
