import logging

from aiogram import Bot
from aiogram.types import WebAppInfo, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiolimiter import AsyncLimiter

from point.config import settings
from point.i18 import translate
from point.view import InvoiceRequest


class BotService:
    def __init__(self):
        self.bot = Bot(token=settings.bot_token)
        self._global_limiter = AsyncLimiter(max_rate=30, time_period=1)
        self.point_app_url = str(settings.point_app_url)

    async def create_invoice_link(self, request: InvoiceRequest) -> str:
        return await self.bot.create_invoice_link(**request.model_dump(mode="json"))

    async def send_message(self, text: str, user_id: int, reply_markup: InlineKeyboardMarkup) -> None:
        async with self._global_limiter:
            try:
                await self.bot.send_message(
                    chat_id=user_id,
                    text=text,
                    parse_mode="HTML",
                    reply_markup=reply_markup,
                )
            except Exception as e:
                logging.exception(f"Error while send message {text} to {user_id}: {e}")

    async def send_message_with_app(self, text: str, user_id: int) -> None:
        builder = InlineKeyboardBuilder().button(
            text=translate(tag_or_text="app", domain="common.keyboards"),
            web_app=WebAppInfo(url=self.point_app_url)
        )

        await self.send_message(
            text=text,
            user_id=user_id,
            reply_markup=builder.as_markup(),
        )


bs = BotService()
