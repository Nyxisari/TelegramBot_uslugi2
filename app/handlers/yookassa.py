import os, json
from aiogram import Router, Dispatcher
from aiogram.client import bot
from aiogram.types import Message, LabeledPrice
from config import settings

dp = Dispatcher()

@dp.message(lambda msg: msg.text == 'Оплатить')
async def send_invoice_handler(message: Message):
    provider_data = {
        "receipt": {
            "items": [{
                "description": "Бронирование фотосессии",
                "quantity": "1.00",
                "amount": {
                    "value": f"{settings.PRICE / 100:.2f}",
                    "currency": 'RUB'
                },
                "vat_code": 1  # 1 = НДС не облагается (для самозанятых)
            }]
        }
    }
    await bot.SendInvoice(chat_id=message.chat.id,
                           title="Фотосессия",
                           discription= "Бронирование фотосессии",
                           payload=f'ps_{message.chat.id}',
                           provider_token=settings.YOOKASSA_TOKEN,
                           currency="RUB",
                           price=[LabeledPrice(label='Стоимость', amount=settings.PRICE)],
                           provider_data=json.dumps(provider_data))