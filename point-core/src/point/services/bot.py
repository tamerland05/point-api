import hashlib
import hmac
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    WebAppInfo,
    InlineKeyboardMarkup,
    Message,
    Update,
    PreCheckoutQuery,
    InlineQueryResultPhoto,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiolimiter import AsyncLimiter

from point.config import settings, AppEnv
from point.i18 import translate
from point.view import InvoiceRequest, Button

dp = Dispatcher()


class BotService:
    def __init__(self):
        self.bot = Bot(
            token=settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self._global_limiter = AsyncLimiter(max_rate=30, time_period=1)
        self._secret_key = hmac.new(b'WebAppData', settings.bot_token.encode('utf-8'), hashlib.sha256).digest()

        self.point_app_url = str(settings.point_app_url)
        self.point_channel_url = "t.me/" + settings.point_channel_name

    async def create_invoice_link(self, request: InvoiceRequest) -> str:
        return await self.bot.create_invoice_link(**request.model_dump(mode="json"))

    async def request(self, func, **kwargs):
        async with self._global_limiter:
            try:
                return await func(**kwargs)
            except Exception as e:
                logging.exception(f"Error while send request with kwargs {kwargs}: {e}")

    async def send_message_with_intro(self, text: str, user_id: int, lang: str) -> None:
        builder = InlineKeyboardBuilder()
        builder.button(
            text=translate(tag_or_text="app", domain="common.keyboards", lang=lang),
            web_app=WebAppInfo(url=self.point_app_url)
        )
        builder.button(
            text=translate(tag_or_text="channel", domain="common.keyboards", lang=lang),
            url=self.point_channel_url,
        )
        builder.adjust(1, repeat=True)

        await self.request(
            func=self.bot.send_message,
            chat_id=user_id,
            text=text,
            reply_markup=builder.as_markup(),
        )

    async def prepare_inline_message(self, user_id: int, text: str, photo: str | None, buttons: list[Button]) -> str:
        if buttons:
            reply_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=b.text, url=str(b.url))]
                    for b in buttons
                ]
            )
        else:
            reply_markup = None

        if photo:
            prepared_message = InlineQueryResultPhoto(
                id=self.make_result_id(text + photo),
                photo_url=photo,
                thumbnail_url=photo,
                caption=text,
                reply_markup=reply_markup,
            )
        else:
            prepared_message = InlineQueryResultArticle(
                id=self.make_result_id(text),
                title="Share",
                input_message_content=InputTextMessageContent(message_text=text),
                reply_markup=reply_markup,
            )

        message = await self.request(
            func=self.bot.save_prepared_inline_message,
            user_id=user_id,
            result=prepared_message,
            allow_user_chats=True,
            allow_bot_chats=True,
            allow_group_chats=True,
            allow_channel_chats=True,
        )

        return message.id

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

    @staticmethod
    def make_result_id(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()


bs = BotService()


@dp.message(CommandStart())
async def handle_start(message: Message) -> None:
    lang = message.from_user.language_code
    await bs.send_message_with_intro(
        text=translate(tag_or_text="start", domain="common.replies", lang=lang),
        user_id=message.from_user.id,
        lang=lang
    )


@dp.pre_checkout_query()
async def handle_pre_checkout(query: PreCheckoutQuery) -> None:
    await query.bot.answer_pre_checkout_query(query.id, ok=True)
