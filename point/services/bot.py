from aiogram import Bot

from point.config import settings
from point.view import InvoiceRequest


class BotService:
    def __init__(self):
        self.bot = Bot(token=settings.bot_token)

    async def create_invoice_link(self, request: InvoiceRequest) -> str:
        return await self.bot.create_invoice_link(**request.model_dump(mode="json"))


bs = BotService()
