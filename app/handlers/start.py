from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from keyboards.start_menu import keyboard_start

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(text="Здравствуйте я — начинающий фотограф, меня зовут Олег.\n"
                         "Фотографией увлекаюсь уже более 3-х лет. За это время снимал пейзажи,"
                         "городские улицы, архитектуру и различные сюжеты.\n"
                         "Опыт работы с людьми пока небольшой — в основном это съёмка мероприятий.\n"
                         "Сейчас я активно развиваюсь в портретной фотографии, хочу наработать опыт,"
                         "пополнить портфолио и создавать качественные, живые фотографии.\n"
                         "Буду рад сотрудничеству и сделаю всё, чтобы съёмка прошла комфортно, а результат оправдал ваши ожидания.", reply_markup=keyboard_start)