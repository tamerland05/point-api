import hashlib
import hmac
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, Message, Update, PreCheckoutQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiolimiter import AsyncLimiter

from point.config import settings, AppEnv
from point.i18 import translate
from point.view import InvoiceRequest

dp = Dispatcher()


class BotService:
    def __init__(self):
        self.bot = Bot(token=settings.bot_token)
        self._global_limiter = AsyncLimiter(max_rate=30, time_period=1)
        self.point_app_url = str(settings.point_app_url)
        self._secret_key = hmac.new(b'WebAppData', settings.bot_token.encode('utf-8'), hashlib.sha256).digest()

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

    async def send_message_with_intro(self, text: str, user_id: int, lang: str) -> None:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=translate(tag_or_text="app", domain="common.keyboards", lang=lang),
            web_app=WebAppInfo(url=self.point_app_url)
        )
        builder.button(
            text=translate(tag_or_text="channel", domain="common.keyboards", lang=lang),
            web_app=WebAppInfo(url=self.point_app_url)
        )
        builder.adjust(1, repeat=True)

        await self.send_message(
            text=text,
            user_id=user_id,
            reply_markup=builder.as_markup(),
        )

    async def feed_update(self, update: Update) -> None:
        await dp.feed_update(self.bot, update)

    def validate_data(self, data_dict: dict) -> bool:
        if settings.app_env == AppEnv.DEV:
            return True

        if "hash" not in data_dict:
            return False
        data_hash = data_dict.pop('hash')

        data_check_array = [f"{key}={value}" for key, value in data_dict.items()]
        data_check_array.sort()
        data = '\n'.join(data_check_array).encode('utf-8')

        calculated_hash = hmac.new(self._secret_key, data, hashlib.sha256).hexdigest()
        return hmac.compare_digest(calculated_hash, data_hash)


bs = BotService()


@dp.message(CommandStart())
async def handle_start(message: Message) -> None:
    lang = "ru"
    await bs.send_message_with_intro(
        text=translate(tag_or_text="start", domain="common.replies", lang=lang),
        user_id=message.from_user.id,
        lang=lang
    )


@dp.pre_checkout_query()
async def handle_pre_checkout(query: PreCheckoutQuery) -> None:
    await query.bot.answer_pre_checkout_query(query.id, ok=True)
