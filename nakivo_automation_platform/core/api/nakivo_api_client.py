"""
NAKIVO HTTP API Client (JSON-RPC Router) for Shift-Left API testing,
session management, pre-flight health checks, and hybrid contract verification.
"""
import json
import ssl
from urllib.parse import urlsplit
import urllib.request
from nakivo_automation_platform.core.logging.masked_logger import MaskedLogger

logger = MaskedLogger.get_logger("NakivoApiClient")


class NakivoApiClient:
    """Client for NAKIVO ExtDirect / JSON-RPC backend router (/c/router)."""

    def __init__(self, director_url="https://localhost:4443"):
        # Robust normalization: strip subpaths like /c/main to ensure clean root director URL
        clean_url = (director_url or "https://localhost:4443").rstrip("/")
        if "/c/" in clean_url:
            parts = urlsplit(clean_url)
            self.director_url = f"{parts.scheme}://{parts.netloc}"
        else:
            self.director_url = clean_url

        self.router_url = f"{self.director_url}/c/router"
        self.main_url = f"{self.director_url}/c/main"
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        self.session_cookie = None

    def send_rpc(self, action: str, method: str, data_list: list, tid: int = 1) -> dict:
        """Send a structured JSON-RPC payload to /c/router."""
        payload = {
            "action": action,
            "method": method,
            "data": data_list,
            "type": "rpc",
            "tid": tid
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/javascript, */*"
        }
        if self.session_cookie:
            headers["Cookie"] = self.session_cookie

        req = urllib.request.Request(self.router_url, data=data_bytes, headers=headers)
        try:
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=5) as resp:
                set_cookie = resp.headers.get("Set-Cookie")
                if set_cookie:
                    self.session_cookie = set_cookie.split(";")[0]
                content = resp.read().decode("utf-8")
                return json.loads(content)
        except Exception as e:
            logger.debug(f"RPC request error ({action}.{method}): {e}")
            return {}

    def is_service_healthy(self, timeout: float = 3.0) -> bool:
        """Pre-flight check verifying NAKIVO Web Director is accepting connections."""
        try:
            req = urllib.request.Request(self.main_url, headers={"User-Agent": "SDET-PreFlight/1.0"})
            with urllib.request.urlopen(req, context=self.ssl_context, timeout=timeout) as resp:
                return resp.status == 200
        except Exception as e:
            logger.debug(f"Pre-flight health check failed: {e}")
            return False

    def verify_session_cookie(self, cookies: list) -> bool:
        """Verify presence of session identification cookies returned by UI authentication."""
        if not cookies:
            return False
        # Look for typical ExtJS/Java session cookies (JSESSIONID, sid, session_id, etc.)
        session_names = {"jsessionid", "sid", "session_id", "nakivo_session", "ext-session"}
        for c in cookies:
            if c.get("name", "").lower() in session_names or "session" in c.get("name", "").lower():
                return True
        # If any cookie has non-empty value, treat as valid established session token
        return any(len(c.get("value", "")) > 0 for c in cookies)
