import asyncio
import logging
from decimal import Decimal, InvalidOperation
from uuid import UUID

import aiohttp
from async_lru import alru_cache

from point.config import settings
from point.controllers.base import BaseController
from point.errors import ErrorCode
from point.models import Asset


class AssetController(BaseController[Asset]):
    error_code: ErrorCode = ErrorCode.ASSET_NOT_FOUND
    model = Asset

    assets_url = str(settings.assets_url)

    @classmethod
    @alru_cache(ttl=60)
    async def get_asset(cls, asset_id: UUID) -> model:
        return await cls.get(id=asset_id, enabled=True)

    @classmethod
    @alru_cache(maxsize=1, ttl=60)
    async def get_all_assets(cls) -> list[model]:
        return await cls.filter(enabled=True).order_by("-priority")

    @classmethod
    @alru_cache(maxsize=1, ttl=30)
    async def get_ton(cls) -> model:
        return await cls.get(symbol="TON", enabled=True)

    @classmethod
    async def update_prices(cls) -> None:
        try:
            assets = await cls.filter(enabled=True)
            assets_prices = await cls._get_assets_prices([asset.address for asset in assets])
            update_tasks = []

            for asset in assets:
                if asset.address not in assets_prices:
                    logging.warning(f"Asset {asset.address} is not prised.")
                new_price = cls._safe_decimal(assets_prices.get(asset.address, "0"))
                if asset.price == new_price:
                    continue
                asset.price = new_price
                update_tasks.append(asset.save(update_fields=["price", "updated_at"]))

            if len(update_tasks) > 0:
                await asyncio.gather(*update_tasks)
        except Exception as e:
            logging.exception(f"Exception while update prices: {e}")

    @classmethod
    async def _get_assets_prices(cls, assets: list[str]) -> dict[str, Decimal]:
        price_key = "dex_price_usd"
        url = cls.assets_url + f"assets/query?" + "".join(f"unconditional_asset={a}&" for a in assets)

        async with aiohttp.ClientSession(base_url=cls.assets_url) as session:
            async with session.post(url=url) as response:
                data = await response.json()
                asset_list = data.get("asset_list", [])
        return {asset["contract_address"]: asset[price_key] for asset in asset_list if price_key in asset}

    @classmethod
    def _safe_decimal(cls, val: str) -> Decimal:
        try:
            return Decimal(val)
        except (InvalidOperation, ValueError, TypeError):
            return Decimal("0")
