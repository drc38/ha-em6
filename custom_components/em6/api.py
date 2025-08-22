"""em6 API helper."""

from __future__ import annotations

import asyncio
import logging
from typing import List, Optional

import aiohttp

_LOGGER = logging.getLogger(__name__)


class em6Api:
    """Simple API wrapper for the em6 data API."""

    _URL_BASE = "https://api.em6.co.nz/ords/em6/data_api/"

    def __init__(self, location: Optional[str] = None) -> None:
        self._location = location

    @staticmethod
    async def _async_get_region_prices() -> Optional[dict]:
        headers = {
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.54"
            )
        }
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(em6Api._URL_BASE + "region/price", headers=headers) as response:
                    if response.status != 200:
                        _LOGGER.error("Failed to fetch data: status %s", response.status)
                        return None
                    return await response.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:  # pragma: no cover - network error
            _LOGGER.error("Failed to fetch data: %s", err)
            return None

    @classmethod
    async def async_get_locations(cls) -> List[str]:
        """Return a list of available grid zone names."""
        data = await cls._async_get_region_prices()
        if not data or "items" not in data:
            return []
        return [item["grid_zone_name"] for item in data["items"]]

    async def async_get_prices(self) -> Optional[dict]:
        """Fetch the current price for the configured location."""
        if not self._location:
            _LOGGER.error("Location not set for price lookup")
            return None
        data = await self._async_get_region_prices()
        if not data:
            return None
        for item in data.get("items", []):
            if item["grid_zone_name"] == self._location:
                return item
        _LOGGER.warning("Location %s not found in API response", self._location)
        return None
