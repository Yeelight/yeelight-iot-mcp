import httpx
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from config.config import settings
from config.region import RegionError, api_base_for_region, resolve_region
from config.yeelight_ai import ProfileError, is_local_profile_allowed, load_cloud_profile
from service.request_context import (
    CloudContext,
    CredentialBundle,
    first_pro_house_id,
)
from utils.auth import (
    extract_token_claims,
    normalize_authorization_header,
    resolve_upstream_client_id,
)


class AuthMiddleware(BaseHTTPMiddleware):
    async def check_token_valid(self, token: str, api_base_url: str) -> bool:
        url = f"{api_base_url}/apis/account/user/info"
        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.get(
                    url,
                    headers={"authorization": normalize_authorization_header(token)},
                )
            return str(response.json().get("code")) == "200"
        except Exception:
            return False

    async def resolve_first_house(self, authorization: str, api_base_url: str) -> str | None:
        url = f"{api_base_url}/apis/iot/v1/house/r/list"
        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT) as client:
                response = await client.get(
                    url,
                    headers={"authorization": authorization, "bizType": "0"},
                )
            return first_pro_house_id(response.json())
        except Exception:
            return None

    async def dispatch(self, request: Request, call_next):
        try:
            credentials = self._resolve_credentials(request)
        except ProfileError as error:
            return JSONResponse({"error": str(error)}, status_code=401)
        if credentials is None:
            return JSONResponse({"error": "缺少或无效的 Token"}, status_code=401)

        claims = extract_token_claims(credentials.authorization)
        region_hint = credentials.region or claims.region
        if credentials.source == "yeelight-ai":
            region_hint = claims.region or credentials.region
        try:
            region = resolve_region(region_hint, settings.DEFAULT_REGION)
            api_base_url = api_base_for_region(
                region,
                settings.API_BASE_URL,
                settings.DEFAULT_REGION,
            )
        except RegionError as error:
            return JSONResponse({"error": str(error)}, status_code=400)

        authorization = normalize_authorization_header(credentials.authorization)
        if not await self.check_token_valid(authorization, api_base_url):
            return JSONResponse({"error": "Token 无效、已过期或与 Region 不匹配"}, status_code=401)

        house_id = credentials.house_id
        if not house_id:
            house_id = await self.resolve_first_house(authorization, api_base_url)
        if not house_id:
            return JSONResponse(
                {"error": "当前 Region 没有可用的 Pro 家庭，请在 Yeelight Pro APP 中创建或加入家庭后重新扫码。"},
                status_code=400,
            )

        request.state.cloud_context = CloudContext(
            authorization=authorization,
            region=region,
            api_base_url=api_base_url,
            house_id=house_id,
            client_id=resolve_upstream_client_id(claims.client_id, region),
            credential_source=credentials.source,
        )
        return await call_next(request)

    def _resolve_credentials(self, request: Request) -> CredentialBundle | None:
        token = request.headers.get(settings.AUTHORIZATION_HEADER_KEY)
        if token:
            return CredentialBundle(
                authorization=token,
                region=request.headers.get(settings.REGION_HEADER_KEY),
                house_id=request.headers.get(settings.HOUSE_ID_HEADER_KEY),
                source="header",
            )
        if not is_local_profile_allowed(settings.RUNTIME_ENV, settings.BIND_HOST):
            return None
        profile = load_cloud_profile()
        return CredentialBundle(
            authorization=profile.authorization,
            region=profile.region,
            house_id=profile.house_id,
            source="yeelight-ai",
        )
