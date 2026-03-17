import logging

logger = logging.getLogger(__name__)

_API_KEY: str = ""
_URL: str = "https://api.sharkeyes.dev/api/v2/server-verify"
_TIMEOUT: float = 5.0


def configure(api_key: str, url: str = None, timeout: float = None):
    global _API_KEY, _URL, _TIMEOUT
    _API_KEY = api_key
    if url:
        _URL = url
    if timeout:
        _TIMEOUT = timeout


def verify(token: str) -> tuple:

    if not _API_KEY:
        raise RuntimeError("First, call sharkeyes.configure(api_key='...')")

    if not token or not token.strip():
        return False, "Enable JavaScript."

    try:
        import httpx

        resp = httpx.post(
            _URL,
            json={"verification_token": token.strip()},
            headers={"X-Api-Key": _API_KEY},
            timeout=_TIMEOUT,
        )

        if resp.status_code != 200:
            return False, "Verification error."

        data = resp.json()

        if data.get("is_bot"):
            return False, data.get("reason", "Verification failed.")

        return True, None

    except Exception as e:
        logger.error("[SharkEyes] %s", e)
        return False, "Technical error during verification."
