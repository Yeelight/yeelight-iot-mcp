import httpx
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("utils.http")

class HttpClient:
    """
    基础HTTP工具类，支持GET和POST请求，自动处理异常和日志。
    """
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
        try:
            response = httpx.get(url, headers=headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"HTTP GET 请求失败: {url}, 错误: {e}")
            return {"error": str(e)}

    def post(self, url: str, headers: Optional[Dict[str, str]] = None, data: Optional[Any] = None, json: Optional[Any] = None) -> Any:
        try:
            response = httpx.post(url, headers=headers, data=data, json=json, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"HTTP POST 请求失败: {url}, 错误: {e}")
            return {"error": str(e)}
