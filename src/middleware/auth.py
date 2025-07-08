from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from config.config import settings
import httpx

class AuthMiddleware(BaseHTTPMiddleware):

    async def check_token_valid(self, token):
        url = f"{settings.API_BASE_URL}/apis/account/user/info"
        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
            response = await client.get(url, headers={"authorization": f"Bearer {token}"})
        if response.json().get("code") != "200":
            return {"error": response.json()}
        return True

    async def dispatch(self, request: Request, call_next):
        token = request.headers.get(settings.AUTHORIZATION_HEADER_KEY)
        if not token:
            return JSONResponse({"error": "缺少或无效的Token"}, status_code=401)
        if not await self.check_token_valid(token):
            return JSONResponse({"error": "Token无效或已过期"}, status_code=401)
        return await call_next(request)