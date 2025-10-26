import asyncio
from decimal import Decimal
from typing import Any
from uuid import UUID

import aiohttp
from fastapi_pagination import Page
from pydantic import AnyUrl

from point.entity_types import PointHash, RecipientType, Image, TaskIntegrationType
from point.view import *
from point.view.common import ViewPortSize


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
        data = {} if data is None else data.model_dump(mode="json", exclude_none=True)

        async with aiohttp.ClientSession(headers=self.headers) as session, session.delete(url=url, data=data) as resp:
            return await self.log_or_return(resp)


class AdminPointApiService(BaseApiService):
    def __init__(self, admin_auth_api_key: str, origin: str) -> None:
        headers = {"AdminApiKey": admin_auth_api_key}
        super().__init__(headers, origin + "/admin")

    async def upload_file(self, file) -> PointHash | None:
        url = self.base_url + "/common/upload-file"
        data = {"file": file}

        async with aiohttp.ClientSession(headers=self.headers) as session, session.post(url, data=data) as resp:
            return await self.log_or_return(resp)

    async def upload_files(self, files: list) -> list[PointHash | None]:
        return await asyncio.gather(*[self.upload_file(file) for file in files])

    async def upload_file_by_path(self, filepath: str) -> PointHash | None:
        with open(filepath, "rb") as f:
            return await self.upload_file(file=f)

    async def upload_files_by_paths(self, filepaths: list[str]) -> list[PointHash | None]:
        return await asyncio.gather(*[self.upload_file_by_path(filepath) for filepath in filepaths])

    async def get_task(self, task_id: str) -> TaskAdminOut:
        resp = await self._get(url="/earn/task/" + task_id)
        return TaskAdminOut.model_validate(resp)

    async def get_all_tasks(self) -> list[TaskAdminOut]:
        resp = await self._get(url="/earn/tasks")
        return TaskAdminOut.list_validate(resp)

    async def create_task(
            self,
            title: str,
            description: str,
            profit: int,
            icon_hash: PointHash,
            link: str,
            integration_type: TaskIntegrationType,
    ) -> TaskAdminOut:
        resp = await self._post(
            url="/earn/task",
            data=TaskCreateIn(
                title=title,
                description=description,
                profit=profit,
                icon_hash=icon_hash,
                link=AnyUrl(link),
                integration_type=integration_type,
            )
        )
        return TaskAdminOut.model_validate(resp)

    async def update_task(
            self,
            task_id: str,
            title: str | None = None,
            description: str | None = None,
            profit: int | None = None,
            icon_hash: PointHash | None = None,
            link: str | None = None,
            integration_type: TaskIntegrationType | None = None,
            enabled: bool | None = None,
    ) -> TaskAdminOut:
        resp = await self._put(
            url="/earn/task/" + task_id,
            data=TaskUpdateIn(
                title=title,
                description=description,
                profit=profit,
                icon_hash=icon_hash,
                link=AnyUrl(link),
                integration_type=integration_type,
                enabled=enabled,
            ),
        )
        return TaskAdminOut.model_validate(resp)

    async def delete_task(self, task_id: str) -> None:
        await self._delete(url="/earn/task/" + task_id)

    async def get_establishment_type(self, establishment_type_id: str) -> EstablishmentTypeAdminOut:
        resp = await self._get(url="/map/establishment-type/" + establishment_type_id)
        return EstablishmentTypeAdminOut.model_validate(resp)

    async def get_all_establishment_types(self) -> list[EstablishmentTypeAdminOut]:
        resp = await self._get(url="/map/establishment-types")
        return EstablishmentTypeAdminOut.list_validate(resp)

    async def create_establishment_type(
            self,
            name: str,
            path_to_icon: str = None,
            icon_hash: PointHash | None = None,
            color_code: str | None = None,
    ) -> EstablishmentTypeAdminOut:
        if icon_hash is None and path_to_icon is not None:
            icon_hash = await self.upload_file_by_path(path_to_icon)

        resp = await self._post(
            url="/map/establishment-type",
            data=EstablishmentTypeCreateIn(name=name, icon_hash=icon_hash, color_code=color_code),
        )
        return EstablishmentTypeAdminOut.model_validate(resp)

    async def update_establishment_type(
            self,
            establishment_type_id: str,
            name: str | None = None,
            icon_hash: PointHash | None = None,
            path_to_icon: str | None = None,
            color_code: str | None = None,
            enabled: bool | None = None,
    ) -> EstablishmentTypeAdminOut:
        if icon_hash is None and path_to_icon is not None:
            icon_hash = await self.upload_file_by_path(path_to_icon)

        resp = await self._put(
            url="/map/establishment-type/" + establishment_type_id,
            data=EstablishmentTypeUpdateIn(name=name, icon_hash=icon_hash, color_code=color_code, enabled=enabled),
        )
        return EstablishmentTypeAdminOut.model_validate(resp)

    async def delete_establishment_type(self, establishment_type_id: str) -> None:
        await self._delete(url="/map/establishment-type/" + establishment_type_id)

    async def get_establishment(self, establishment_id: str) -> EstablishmentAdminOut:
        resp = await self._get(url="/map/establishment/" + establishment_id)
        return EstablishmentAdminOut.model_validate(resp)

    async def get_all_establishments(
            self,
            name_contains: str | None = None,
            establishment_type_id: str | None = None,
            page: int | None = None,
            size: int | None = None,
            sort: list[EstablishmentSortOrder] | None = None,
    ) -> Page[EstablishmentAdminOut]:
        resp = await self._post(
            url="/map/establishments",
            data=EstablishmentCriteria(
                name_contains=name_contains,
                establishment_type_id=establishment_type_id,
                page=page,
                size=size,
                sort=sort,
            )
        )
        return Page.model_validate(resp)

    async def create_establishment(
            self,
            establishment_type_id: str,
            latitude: Decimal,
            longitude: Decimal,
            address: str,
            name: str,
            description: str,
            icon_hash: PointHash | None = None,
            path_to_icon: str | None = None,
            photo_hash: PointHash | None = None,
            path_to_photo: str | None = None,
            paths_to_gallery: list[str] | None = None,
            gallery_hashes: list[PointHash] | None = None,
            channel_link: str | None = None,
    ) -> EstablishmentAdminOut:
        if icon_hash is None and path_to_icon is not None:
            icon_hash = await self.upload_file_by_path(path_to_icon)
        if photo_hash is None and path_to_photo is not None:
            photo_hash = await self.upload_file_by_path(path_to_photo)
        if gallery_hashes is None and paths_to_gallery is not None:
            gallery_hashes = await self.upload_files_by_paths(paths_to_gallery)

        resp = await self._post(
            url="/map/establishment",
            data=EstablishmentCreateIn(
                establishment_type_id=UUID(establishment_type_id),
                longitude=longitude,
                latitude=latitude,
                address=address,
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
            gallery_hashes: list[PointHash] | None = None,
            channel_link: str | None = None,
            enabled: bool | None = None,
    ) -> EstablishmentAdminOut:
        if icon_hash is None and path_to_icon is not None:
            icon_hash = await self.upload_file_by_path(path_to_icon)
        if photo_hash is None and path_to_photo is not None:
            photo_hash = await self.upload_file_by_path(path_to_photo)
        if gallery_hashes is None and paths_to_gallery is not None:
            gallery_hashes = await self.upload_files_by_paths(paths_to_gallery)

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
                gallery_hashes=gallery_hashes,
                channel_link=channel_link,
                enabled=enabled,
            ),
        )
        return EstablishmentAdminOut.model_validate(resp)

    async def delete_establishment(self, establishment_id: str) -> None:
        await self._delete(url="/map/establishment/" + establishment_id)

    async def get_menu_item(self, menu_item_id: str) -> MenuItemAdminOut:
        resp = await self._get(url="/map/menu-item/" + menu_item_id)
        return MenuItemAdminOut.model_validate(resp)

    async def get_all_menu_items(self) -> list[MenuItemAdminOut]:
        resp = await self._get(url="/map/menu-items")
        return MenuItemAdminOut.list_validate(resp)

    async def create_menu_item(
            self,
            establishment_id: str,
            category: str,
            title: str,
            description: str,
            cost: Cost,
            photo_hash: PointHash | None = None,
            path_to_photo: str | None = None,
    ) -> MenuItemAdminOut:
        if photo_hash is None:
            photo_hash = None if path_to_photo is None else await self.upload_file_by_path(path_to_photo)
        resp = await self._post(
            url="/map/menu-item",
            data=MenuItemCreateIn(
                establishment_id=UUID(establishment_id),
                category=category,
                title=title,
                description=description,
                photo_hash=photo_hash,
                cost=cost,
            ),
        )
        return MenuItemAdminOut.model_validate(resp)

    async def create_menu_items(
            self,
            establishment_ids: list[str],
            category: str,
            title: str,
            description: str,
            cost: Cost,
            photo_hash: PointHash | None = None,
            path_to_photo: str | None = None,
    ) -> None:
        if photo_hash is None:
            photo_hash = None if path_to_photo is None else await self.upload_file_by_path(path_to_photo)
        for establishment_id in set(establishment_ids):
            await self._post(
                url="/map/menu-item",
                data=MenuItemCreateIn(
                    establishment_id=UUID(establishment_id),
                    category=category,
                    title=title,
                    description=description,
                    photo_hash=photo_hash,
                    cost=cost,
                ),
            )

    async def update_menu_item(
            self,
            menu_item_id: str,
            establishment_id: str | None = None,
            category: str | None = None,
            title: str | None = None,
            description: str | None = None,
            path_to_photo: str | None = None,
            photo_hash: str | None = None,
            amount: Decimal | None = None,
            currency: str | None = None,
            enabled: bool | None = None,
    ) -> MenuItemAdminOut:
        if photo_hash is None and path_to_photo is not None:
            photo_hash = await self.upload_file_by_path(path_to_photo)

        resp = await self._put(
            url="/map/menu-item/" + menu_item_id,
            data=MenuItemUpdateIn(
                establishment_id=establishment_id,
                category=category,
                title=title,
                description=description,
                photo_hash=photo_hash,
                amount=amount,
                currency=currency,
                enabled=enabled,
            ),
        )
        return MenuItemAdminOut.model_validate(resp)

    async def delete_menu_item(self, menu_item_id: str) -> None:
        await self._delete(url="/map/menu-item/" + menu_item_id)

    async def get_all_invitations(self) -> list[InvitationAdminOut]:
        resp = await self._get(url="/account/invitations")
        return InvitationAdminOut.list_validate(resp)

    async def create_invitation(
            self,
            user_id: int,
            establishment_id: str,
    ) -> InvitationAdminOut:
        resp = await self._post(
            url="/account/invitation",
            data=InvitationCreateIn(user_id=user_id, establishment_id=UUID(establishment_id)),
        )
        return InvitationAdminOut.model_validate(resp)

    async def delete_invitation(
            self,
            user_id: int,
            establishment_id: str,
    ) -> None:
        await self._post(
            url="/account/invitation-delete",
            data=InvitationDeleteIn(user_id=user_id, establishment_id=UUID(establishment_id)),
        )

    async def get_purpose_icon(self, purpose_icon_id: str) -> PurposeIconAdminOut:
        resp = await self._get(url="/account/purpose-icon/" + purpose_icon_id)
        return PurposeIconAdminOut.model_validate(resp)

    async def get_all_purpose_icons(self) -> list[PurposeIconAdminOut]:
        resp = await self._get(url="/account/purpose-icons")
        return PurposeIconAdminOut.list_validate(resp)

    async def create_purpose_icon(
            self,
            path_to_icon: str,
            path_to_preview: str
    ) -> PurposeIconAdminOut:
        icon_hash, preview_hash = await self.upload_files_by_paths([path_to_icon, path_to_preview])
        resp = await self._post(
            url="/account/purpose-icon",
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
            icon_hash = await self.upload_file_by_path(path_to_icon)

        if preview_hash is None and path_to_preview is not None:
            preview_hash = await self.upload_file_by_path(path_to_preview)

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
        return AssetAdminOut.list_validate(resp)

    async def create_asset(
            self,
            symbol: str,
            name: str,
            decimals: int,
            address: str,
            image_url: str,
            priority: int
    ) -> AssetAdminOut:
        resp = await self._post(
            url="/tip/asset",
            data=AssetCreateIn(
                symbol=symbol,
                name=name,
                decimals=decimals,
                address=address,
                image_url=Image(image_url),
                priority=priority
            ),
        )
        return AssetAdminOut.model_validate(resp)

    async def update_asset(
            self,
            asset_id: str,
            symbol: str | None = None,
            name: str | None = None,
            decimals: int | None = None,
            address: str | None = None,
            image_url: str | None = None,
            priority: int | None = None,
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
                priority=priority,
                enabled=enabled
            ),
        )
        return AssetAdminOut.model_validate(resp)

    async def delete_asset(self, asset_id: str) -> None:
        await self._delete(url="/tip/asset/" + asset_id)


class PublicPointApiService(BaseApiService):
    current_user: AuthUserOut

    def __init__(self, origin: str) -> None:
        super().__init__({}, origin)

    async def auth(
            self,
            init_data_raw: str,
            referrer_id: int | None = None,
    ) -> None:
        resp = await self._post(
            url="/account/auth",
            data=AuthIn(
                referrer_id=referrer_id,
                init_data_raw=init_data_raw,
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

    async def get_referrals(
            self,
            page: int = 1,
            size: int = 100,
    ) -> Page:
        resp = await self._get(url=f"/earn/referrals?page={page}&size={size}")
        resp["items"] = ReferralOut.list_validate(resp["items"])
        return resp

    async def get_tasks(self) -> list[TaskOut]:
        resp = await self._get(url=f"/earn/tasks")
        return TaskOut.list_validate(resp)

    async def get_top(self) -> list[UserPublicOut]:
        resp = await self._get(url=f"/earn/top")
        return UserPublicOut.list_validate(resp)

    async def get_invitation(self) -> InvitationOut:
        resp = await self._get(url="/account/invitation")
        return InvitationOut.model_validate(resp)

    async def get_purpose_icons(self) -> list[PurposeIconOut]:
        resp = await self._get(url="/account/purpose-icons")
        return PurposeIconOut.list_validate(resp)

    async def create_employee(
            self,
            meta: EmployeeMeta,
            first_name: str,
            last_name: str,
            photo_path: str,
    ):
        create_in = EmployeeCreateIn(
            first_name=first_name,
            last_name=last_name,
            meta=meta,
        )
        form = aiohttp.FormData()
        form.add_field("create_in", create_in.model_dump_json(), content_type="application/json")
        form.add_field(
            'file',
            open(photo_path, 'rb'),
            filename=photo_path,
            content_type='image/svg+xml'
        )

        url = f"{self.base_url}/account/employee"

        async with aiohttp.ClientSession(headers=self.headers) as session, session.post(url=url, data=form) as resp:
            return await self.log_or_return(resp)

    async def update_employee(
            self,
            purpose: PurposeIn | None = None,
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

    async def delete_employee(self) -> None:
        await self._delete(url="/account/employee")

    async def get_establishment_types(self) -> dict[UUID, EstablishmentTypeOut]:
        resp = await self._get(url="/map/establishment-types")
        return {k: EstablishmentTypeOut.model_validate(v) for k, v in resp.items()}

    async def get_establishments(
            self,
            latitude: str,
            longitude: str,
            scale: float,
            view_port_size: ViewPortSize
    ) -> list[EstablishmentPreview]:
        resp = await self._post(
            url="/map/establishments",
            data=PointWithScale(
                latitude=Decimal(latitude),
                longitude=Decimal(longitude),
                scale=scale,
                view_port_size=view_port_size
            )
        )

        return EstablishmentPreview.list_validate(resp)

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

        return EstablishmentPreview.list_validate(resp)

    async def get_establishment(self, establishment_id: str) -> EstablishmentOut:
        resp = await self._get(url="/map/establishment/" + establishment_id)
        return EstablishmentOut.model_validate(resp)

    async def set_establishment_rating(
            self,
            establishment_id: str,
            mark: int,
    ) -> str:
        resp = await self._post(
            url="/map/establishment-rating/create-invoice",
            data=EstablishmentRatingCreateIn(
                establishment_id=UUID(establishment_id),
                mark=mark,
            )
        )
        return resp

    async def get_menu_item(self, menu_item_id: str) -> MenuItemOut:
        resp = await self._get(url="/map/menu-item/" + menu_item_id)
        return MenuItemOut.model_validate(resp)

    async def get_receivers(self, establishment_id: str) -> ReceiversOut:
        resp = await self._get(url="/tip/receivers/" + establishment_id)
        return ReceiversOut.model_validate(resp)

    async def get_assets(self) -> list[AssetOut]:
        resp = await self._get(url="/tip/assets")
        return AssetOut.list_validate(resp)

    async def checkout_tip(
            self,
            recipient_id: str,
            recipient_type: RecipientType,
            asset_id: str,
            amount: str,
    ) -> list[TransactionOut]:
        resp = await self._post(
            url="/tip/send/checkout",
            data=CheckoutTipIn(
                recipient_id=UUID(recipient_id),
                recipient_type=recipient_type,
                asset_id=UUID(asset_id),
                amount=Decimal(amount),
            )
        )
        return TransactionOut.list_validate(resp)


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
