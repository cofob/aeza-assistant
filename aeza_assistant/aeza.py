from aiohttp import ClientSession
from json import dumps

from typing import Any


class Aeza:
    def __init__(self, token: str, session: ClientSession = ClientSession()) -> None:
        self.token = token
        self.session = session
        self.base_url = "https://core.aeza.net/api/"
        self.headers = {
            "X-API-Key": self.token,
        }

    async def _request(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        async with self.session.request(method, self.base_url + url, headers=self.headers, **kwargs) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def get_product_group_statuses(self) -> dict[int, bool]:
        out = {}
        resp = await self._request("GET", "services/groups")
        print(dumps(resp))
        for group in resp["data"]["items"]:
            _id = group["id"]
            if group["group"]["payload"].get("isDisabled") is None:
                out[_id] = False
            else:
                print(group["group"]["payload"]["isDisabled"])
        return out
