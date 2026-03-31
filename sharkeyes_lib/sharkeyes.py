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



def _extract_ip(request):
    if hasattr(request, 'META'):
        x_ff = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_ff:
            return x_ff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
    if hasattr(request, 'headers'):
        x_ff = request.headers.get('x-forwarded-for')
        if x_ff:
            return x_ff.split(',')[0].strip()
        if hasattr(request, 'client') and request.client:
            return request.client.host
    return "127.0.0.1"
    

def verify(token: str) -> tuple:

    if not _API_KEY:
        raise RuntimeError("First, call sharkeyes.configure(api_key='...')")
    user_ip = _extract_ip(request_obj)
    if not token or not token.strip():
        return False, "Enable JavaScript."

    try:
        import httpx

        resp = httpx.post(
            _URL,
            json={
                "verification_token": token.strip(),
                "user_ip": user_ip
            },
            headers={"X-Api-Key": _API_KEY},
            timeout=_TIMEOUT,
        )

        if resp.status_code != 200:
            return False, "Verification error."

        data = resp.json()

        if data.get("is_bot") is False:
            return True, None
            
        return False, data.get("reason", "Verification failed.")


    except Exception as e:
        logger.error("[SharkEyes] %s", e)
        return False, "Technical error during verification."
