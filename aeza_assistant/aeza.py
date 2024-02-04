from logging import getLogger
from typing import Any

from aiohttp import ClientSession

log = getLogger(__name__)


class Aeza:
    def __init__(
        self,
        token: str | None = None,
        session: ClientSession | None = None,
        http_proxy: str | None = None,
    ) -> None:
        self.session = session or ClientSession()
        self.base_url = "https://my.aeza.net/api/"
        self.http_proxy = http_proxy

        self.headers = {}
        if token is not None:
            self.headers["X-API-Key"] = token

    async def _request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        if self.http_proxy is not None:
            kwargs["proxy"] = self.http_proxy
        async with self.session.request(
            method, self.base_url + url, headers=self.headers, **kwargs
        ) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_product_group_statuses(self) -> dict[int, bool]:
        out = {}
        resp = await self._request("GET", "services/products")
        for group in resp["data"]["items"]:
            try:
                id_ = group["id"]
                status = group["group"]["payload"].get("isDisabled", False) in [
                    "true",
                    True,
                ]
                out[id_] = False if status else True
            except (KeyError, TypeError) as e:
                if group is None:
                    continue
                log.debug(
                    f"Error in get_product_group_statuses, id: {group.get('id', 'ID not defined')}: {str(e)}"
                )
        return out
