import asyncio
from decimal import Decimal
from typing import Any
from uuid import UUID

import aiohttp

from point.entity_types import PointHash, RecipientType, Image
from point.view import (
    PointBase,
    EstablishmentTypeCreateIn,
    EstablishmentTypeUpdateIn,
    EstablishmentCreateIn,
    EstablishmentUpdateIn,
    PointUploadIn,
    MenuItemOut,
    Cost,
    MenuItemCreateIn,
    MenuItemUpdateIn,
    EstablishmentTypeAdminOut,
    EstablishmentAdminOut,
    AssetAdminOut,
    AssetCreateIn,
    AssetUpdateIn,
    AuthUserIn,
    AuthIn,
    AuthOut,
    AuthUserOut,
    PointWithScale,
    EstablishmentPreview,
    NearEstablishmentCriteria,
    PointRequestIn,
    EstablishmentOut,
    EstablishmentTypeOut,
    ReceiversOut,
    AssetOut,
    TransactionOut,
    CheckoutTipIn,
    UserMeta,
    UserUpdateIn,
    UserPublicOut,
    PurposeIconAdminOut,
    PurposeIconCreateIn,
    PurposeIconUpdateIn,
    PurposeIconOut,
    PurposeUpdateIn,
    EmployeeMeta,
    EmployeeUpdateIn,
)


class BaseApiService:
    def __init__(self, headers: dict, origin: str) -> None:
        self.headers = headers
        self.base_url = origin

    @staticmethod
    def _build_params(params: PointBase) -> str:
        return "&".join([f"{k}={v}" for k, v in params.model_dump(by_alias=True).items() if v is not None])

    @staticmethod
    async def log_or_return(resp) -> Any | None:
        if resp.status < 400:
            result = await resp.json()
            return result
        else:
            raise Exception(f"point api response {resp.status}: {await resp.text()}")

    async def _get(self, url) -> Any | None:
        url = f"{self.base_url}{url}"

        async with aiohttp.ClientSession(headers=self.headers) as session, session.get(url=url) as resp:
            return await self.log_or_return(resp)

    async def _post(self, url: str, data: PointBase = None) -> Any | None:
        url = f"{self.base_url}{url}"
        data = {} if data is None else data.model_dump(mode="json")

        async with (aiohttp.ClientSession(headers=self.headers) as session, session.post(url=url, json=data) as resp):
            return await self.log_or_return(resp)

    async def _put(self, url: str, data: PointBase = None) -> Any | None:
        url = f"{self.base_url}{url}"
        data = {} if data is None else data.model_dump(mode="json", exclude_none=True)

        async with aiohttp.ClientSession(headers=self.headers) as session, session.put(url=url, json=data) as resp:
            return await self.log_or_return(resp)

    async def _delete(self, url: str, data: PointBase = None) -> Any | None:
        url = f"{self.base_url}{url}"
        data = {} if data is None else data.model_dump_json()

        async with aiohttp.ClientSession(headers=self.headers) as session, session.delete(url=url, data=data) as resp:
            return await self.log_or_return(resp)


class AdminPointApiService(BaseApiService):
    def __init__(self, admin_auth_api_key: str, origin: str) -> None:
        headers = {"AdminApiKey": admin_auth_api_key}
        super().__init__(headers, origin + "/admin")

    async def upload_file(self, filepath: str) -> PointHash | None:
        with open(filepath, 'rb') as f:
            url = self.base_url + "/common/upload-file"
            data = {'file': f}

            async with aiohttp.ClientSession(headers=self.headers) as session, session.post(url, data=data) as resp:
                return await self.log_or_return(resp)

    async def upload_files(self, filepaths: list[str]) -> list[PointHash] | None:
        return await asyncio.gather(*[asyncio.create_task(self.upload_file(filepath)) for filepath in filepaths])

    async def get_establishment_type(self, establishment_type_id: str) -> EstablishmentTypeAdminOut:
        resp = await self._get(url="/map/establishment-type/" + establishment_type_id)
        return EstablishmentTypeAdminOut.model_validate(resp)

    async def get_all_establishment_types(self) -> list[EstablishmentTypeAdminOut]:
        resp = await self._get(url="/map/establishment-types")
        return [EstablishmentTypeAdminOut.model_validate(e) for e in resp]

    async def create_establishment_type(self, name: str, path_to_icon: str) -> EstablishmentTypeAdminOut:
        icon_hash = await self.upload_file(path_to_icon)
        resp = await self._post(
            url="/map/establishment-type",
            data=EstablishmentTypeCreateIn(name=name, icon_hash=icon_hash),
        )
        return EstablishmentTypeAdminOut.model_validate(resp)

    async def update_establishment_type(
            self,
            establishment_type_id: str,
            name: str | None = None,
            icon_hash: PointHash | None = None,
            path_to_icon: str | None = None,
            enabled: bool | None = None,
    ) -> EstablishmentTypeAdminOut:
        if icon_hash is None and path_to_icon is not None:
            icon_hash = await self.upload_file(path_to_icon)

        resp = await self._put(
            url="/map/establishment-type/" + establishment_type_id,
            data=EstablishmentTypeUpdateIn(name=name, icon_hash=icon_hash, enabled=enabled),
        )
        return EstablishmentTypeAdminOut.model_validate(resp)

    async def delete_establishment_type(self, establishment_type_id: str) -> None:
        await self._delete(url="/map/establishment-type/" + establishment_type_id)

    async def get_establishment(self, establishment_id: str) -> EstablishmentAdminOut:
        resp = await self._get(url="/map/establishment/" + establishment_id)
        return EstablishmentAdminOut.model_validate(resp)

    async def get_all_establishments(self) -> list[EstablishmentAdminOut]:
        resp = await self._get(url="/map/establishments")
        return [EstablishmentAdminOut.model_validate(e) for e in resp]

    async def create_establishment(
            self,
            establishment_type_id: str,
            position: PointUploadIn,
            name: str,
            description: str,
            path_to_icon: str,
            path_to_photo: str,
            paths_to_gallery: list[str],
            channel_link: str | None = None,
    ) -> EstablishmentAdminOut:
        icon_hash, photo_hash = await self.upload_files([path_to_icon, path_to_photo])
        gallery_hashes = await self.upload_files(paths_to_gallery)  # можно сделать, чтобы указывалась директория
        resp = await self._post(
            url="/map/establishment",
            data=EstablishmentCreateIn(
                establishment_type_id=UUID(establishment_type_id),
                position=position,
                name=name,
                description=description,
                icon_hash=icon_hash,
                photo_hash=photo_hash,
                gallery_hashes=gallery_hashes,
                channel_link=channel_link,
            ),
        )
        return EstablishmentAdminOut.model_validate(resp)

    async def update_establishment(
            self,
            establishment_id: str,
            establishment_type_id: str | None = None,
            latitude: Decimal | None = None,
            longitude: Decimal | None = None,
            address: str | None = None,
            name: str | None = None,
            description: str | None = None,
            icon_hash: PointHash | None = None,
            path_to_icon: str | None = None,
            photo_hash: PointHash | None = None,
            path_to_photo: str | None = None,
            paths_to_gallery: list[str] | None = None,
            gallery: list[PointHash] | None = None,
            channel_link: str | None = None,
            enabled: bool | None = None,
    ) -> EstablishmentAdminOut:
        if icon_hash is None and path_to_icon is not None:
            icon_hash = await self.upload_file(path_to_icon)
        if photo_hash is None and path_to_photo is not None:
            photo_hash = await self.upload_file(path_to_photo)
        if gallery is None and paths_to_gallery is not None:
            gallery = await self.upload_files(paths_to_gallery)

        resp = await self._put(
            url="/map/establishment/" + establishment_id,
            data=EstablishmentUpdateIn(
                establishment_type_id=UUID(establishment_type_id),
                latitude=latitude,
                longitude=longitude,
                address=address,
                name=name,
                description=description,
                icon_hash=icon_hash,
                photo_hash=photo_hash,
                gallery=gallery,
                channel_link=channel_link,
                enabled=enabled,
            ),
        )
        return EstablishmentAdminOut.model_validate(resp)

    async def delete_establishment(self, establishment_id: str) -> None:
        await self._delete(url="/map/establishment/" + establishment_id)

    async def get_menu_item(self, menu_item_id: str) -> MenuItemOut:
        resp = await self._get(url="/map/menu-item/" + menu_item_id)
        return MenuItemOut.model_validate(resp)

    async def get_all_menu_items(self) -> list[MenuItemOut]:
        resp = await self._get(url="/map/menu-items")
        return [MenuItemOut.model_validate(m) for m in resp]

    async def create_menu_item(
            self,
            establishment_id: str,
            title: str,
            description: str,
            path_to_photo: str,
            cost: Cost,
    ) -> MenuItemOut:
        photo_hash = await self.upload_file(path_to_photo)
        resp = await self._post(
            url="/map/menu-item",
            data=MenuItemCreateIn(
                establishment_id=UUID(establishment_id),
                title=title,
                description=description,
                photo_hash=photo_hash,
                cost=cost,
            ),
        )
        return MenuItemOut.model_validate(resp)

    async def update_menu_item(
            self,
            menu_item_id: str,
            establishment_id: str | None = None,
            title: str | None = None,
            description: str | None = None,
            path_to_photo: str | None = None,
            photo_hash: str | None = None,
            amount: Decimal | None = None,
            currency: str | None = None,
            enabled: bool | None = None,
    ) -> MenuItemOut:
        if photo_hash is None and path_to_photo is not None:
            photo_hash = await self.upload_file(path_to_photo)

        resp = await self._put(
            url="/map/menu-item/" + menu_item_id,
            data=MenuItemUpdateIn(
                establishment_id=establishment_id,
                title=title,
                description=description,
                photo_hash=photo_hash,
                amount=amount,
                currency=currency,
                enabled=enabled,
            ),
        )
        return MenuItemOut.model_validate(resp)

    async def delete_menu_item(self, menu_item_id: str) -> None:
        await self._delete(url="/map/menu-item/" + menu_item_id)

    async def get_purpose_icon(self, purpose_icon_id: str) -> PurposeIconAdminOut:
        resp = await self._get(url="/account/purpose-icon/" + purpose_icon_id)
        return PurposeIconAdminOut.model_validate(resp)

    async def get_all_purpose_icons(self) -> list[PurposeIconAdminOut]:
        resp = await self._get(url="/account/purpose-icons")
        return [PurposeIconAdminOut.model_validate(p) for p in resp]

    async def create_purpose_icon(
            self,
            path_to_icon: str,
            path_to_preview: str
    ) -> PurposeIconAdminOut:
        icon_hash, preview_hash = await self.upload_files([path_to_icon, path_to_preview])
        resp = await self._post(
            url="/account/purpose-icon/",
            data=PurposeIconCreateIn(icon_hash=icon_hash, preview_hash=preview_hash),
        )
        return PurposeIconAdminOut.model_validate(resp)

    async def update_purpose_icon(
            self,
            purpose_icon_id: str,
            icon_hash: str | None = None,
            path_to_icon: str | None = None,
            preview_hash: str | None = None,
            path_to_preview: str | None = None,
            enabled: bool | None = None,
    ) -> PurposeIconAdminOut:
        if icon_hash is None and path_to_icon is not None:
            icon_hash = await self.upload_file(path_to_icon)

        if preview_hash is None and path_to_preview is not None:
            preview_hash = await self.upload_file(path_to_preview)

        resp = await self._put(
            url="/account/purpose-icon/" + purpose_icon_id,
            data=PurposeIconUpdateIn(icon_hash=icon_hash, preview_hash=preview_hash, enabled=enabled),
        )
        return PurposeIconAdminOut.model_validate(resp)

    async def delete_purpose_icon(self, purpose_icon_id: str) -> None:
        await self._delete(url="/account/purpose-icon/" + purpose_icon_id)

    async def get_asset(self, asset_id: str) -> AssetAdminOut:
        resp = await self._get(url="/tip/asset/" + asset_id)
        return AssetAdminOut.model_validate(resp)

    async def get_all_assets(self) -> list[AssetAdminOut]:
        resp = await self._get(url="/tip/assets")
        return [AssetAdminOut.model_validate(a) for a in resp]

    async def create_asset(
            self,
            symbol: str,
            name: str,
            decimals: int,
            address: str,
            image_url: str,
    ) -> AssetAdminOut:
        resp = await self._post(
            url="/tip/asset",
            data=AssetCreateIn(
                symbol=symbol,
                name=name,
                decimals=decimals,
                address=address,
                image_url=Image(image_url),
            ),
        )
        return AssetAdminOut.model_validate(resp)

    async def update_asset(
            self,
            asset_id: str | None = None,
            symbol: str | None = None,
            name: str | None = None,
            decimals: int | None = None,
            address: str | None = None,
            image_url: str | None = None,
            enabled: bool | None = None,
    ) -> AssetAdminOut:
        resp = await self._put(
            url="/tip/asset/" + asset_id,
            data=AssetUpdateIn(
                symbol=symbol,
                name=name,
                decimals=decimals,
                address=address,
                image_url=image_url,
                enabled=enabled
            ),
        )
        return AssetAdminOut.model_validate(resp)

    async def delete_asset(self, establishment_type_id: str) -> None:
        await self._delete(url="/tip/asset/" + establishment_type_id)


class PublicPointApiService(BaseApiService):
    current_user: AuthUserOut

    def __init__(self, origin: str) -> None:
        super().__init__({}, origin)

    async def auth(
            self,
            user: AuthUserIn,
            hash: str,
            referrer_data: str | None = None,
    ) -> None:
        resp = await self._post(
            url="/account/auth",
            data=AuthIn(
                hash=hash,
                referrer_data=referrer_data,
                user=user,
            )
        )
        auth_out = AuthOut.model_validate(resp)
        self.headers["Authorization"] = "Bearer " + auth_out.access_token
        self.current_user = auth_out.user

    async def get_user(self, user_id: int) -> UserPublicOut:
        resp = await self._get(url="/account/user/" + str(user_id))
        return UserPublicOut.model_validate(resp)

    async def update_user(
            self,
            wallet: str | None = None,
            meta: UserMeta | None = None,
    ) -> None:
        await self._put(
            url="/account/user",
            data=UserUpdateIn(wallet=wallet, meta=meta,)
        )

    async def get_purpose_icons(self) -> list[PurposeIconOut]:
        resp = await self._get(url="/account/purpose-icons")
        return [PurposeIconOut.model_validate(a) for a in resp]

    async def update_employee(
            self,
            purpose: PurposeUpdateIn | None = None,
            meta: EmployeeMeta | None = None,
            first_name: str | None = None,
            last_name: str | None = None,
            photo_path: str | None = None,
    ) -> None:
        update_in = EmployeeUpdateIn(
            purpose=purpose,
            first_name=first_name,
            last_name=last_name,
            meta=meta,
        )
        form = aiohttp.FormData()
        form.add_field('update_in', update_in.model_dump_json(exclude_none=True), content_type='application/json')

        if photo_path:
            form.add_field(
                'file',
                open(photo_path, 'rb'),
                filename=photo_path,
                content_type='image/svg+xml'
            )

        url = f"{self.base_url}/account/employee"

        async with aiohttp.ClientSession(headers=self.headers) as session, session.put(url=url, data=form) as resp:
            return await self.log_or_return(resp)

    async def get_establishment_types(self) -> dict[UUID, EstablishmentTypeOut]:
        resp = await self._get(url="/map/establishment-types")
        return {k: EstablishmentTypeOut.model_validate(v) for k, v in resp.items()}

    async def get_establishments(
            self,
            latitude: str,
            longitude: str,
            scale: str,
    ) -> list[EstablishmentPreview]:
        resp = await self._post(
            url="/map/establishments",
            data=PointWithScale(
                latitude=Decimal(latitude),
                longitude=Decimal(longitude),
                scale=Decimal(scale),
            )
        )

        return [EstablishmentPreview.model_validate(e) for e in resp]

    async def get_establishments_near(
            self,
            latitude: str,
            longitude: str,
            name: str | None = None,
    ) -> list[EstablishmentPreview]:
        resp = await self._post(
            url="/map/establishments/near",
            data=NearEstablishmentCriteria(
                location=PointRequestIn(
                    latitude=Decimal(latitude),
                    longitude=Decimal(longitude),
                ),
                name=name,
            ),
        )

        return [EstablishmentPreview.model_validate(e) for e in resp]

    async def get_establishment(self, establishment_id: str) -> EstablishmentOut:
        resp = await self._get(url="/map/establishment/" + establishment_id)
        return EstablishmentOut.model_validate(resp)

    async def get_menu_item(self, menu_item_id: str) -> MenuItemOut:
        resp = await self._get(url="/map/menu-item/" + menu_item_id)
        return MenuItemOut.model_validate(resp)

    async def get_receivers(self, establishment_id: str) -> ReceiversOut:
        resp = await self._get(url="/tip/receivers/" + establishment_id)
        return ReceiversOut.model_validate(resp)

    async def get_assets(self) -> list[AssetOut]:
        resp = await self._get(url="/tip/assets")
        return [AssetOut.model_validate(a) for a in resp]

    async def checkout_tip(
            self,
            recipient_id: UUID,
            recipient_type: RecipientType,
            asset_id: UUID,
            amount: str,
    ) -> list[TransactionOut]:
        resp = await self._post(
            url="/tip/send/checkout",
            data=CheckoutTipIn(
                recipient_id=recipient_id,
                recipient_type=recipient_type,
                asset_id=asset_id,
                amount=Decimal(amount),
            )
        )
        return [TransactionOut.model_validate(t) for t in resp]


async def main():
    admin_auth_api_key = ""
    origin = ""

    apas = AdminPointApiService(admin_auth_api_key=admin_auth_api_key, origin=origin)
    ppas = PublicPointApiService(origin=origin)

    # res = apas.any_method(...)
    # res = ppas.any_method(...)
    # print(res)


if __name__ == '__main__':
    asyncio.run(main())
