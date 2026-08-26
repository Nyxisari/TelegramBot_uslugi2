import os, json
from aiogram import Router, Dispatcher
from aiogram import F
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from config import settings

router = Router()

@router.message(lambda msg: msg.text == 'Оплатить')
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
    await message.bot.send_invoice(chat_id=message.chat.id,
                           title="Фотосессия",
                           description= "Бронирование фотосессии",
                           payload=f'ps_{message.chat.id}',
                           provider_token=settings.YOOKASSA_TOKEN,
                           currency="RUB",
                           prices=[LabeledPrice(label='Стоимость', amount=settings.PRICE)],
                           provider_data=json.dumps(provider_data))

@router.pre_checkout_query()
async def checkout_handler(query: PreCheckoutQuery):
    if query.invoice_payload != f'ps_{query.from_user.id}':
        await query.answer(ok=False, error_message="Что то пошло не так.")
    else:
        await query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    payment_data = message.successful_payment
    print(payment_data)
    payment_id = payment_data.telegram_payment_charge_id
    print(payment_id)
    await message.answer(f"Оплата прошла успешно! id: {payment_id}")