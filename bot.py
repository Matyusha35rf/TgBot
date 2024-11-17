import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# Импорт данных из config.py
from config import BOT_TOKEN, ADMIN_ID, ADMIN_USERNAME

# Переменная для хранения статуса
status = "неизвестен"

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Клавиатуры
admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Я в общаге"), KeyboardButton(text="Меня нет в общаге")]
    ],
    resize_keyboard=True
)

user_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Узнать где Матвей")],
        [KeyboardButton(text="Связаться")]
    ],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    """
    Обработчик команды /start.
    """
    if message.from_user.id == ADMIN_ID:
        await message.answer("Привет, Матвей! Используй кнопки для обновления статуса.", reply_markup=admin_kb)
    else:
        await message.answer("Привет! Нажмите кнопку, чтобы узнать, где Матвей, или связаться с ним.", reply_markup=user_kb)


@dp.message(lambda message: message.text in ["Я в общаге", "Меня нет в общаге"])
async def status_update(message: types.Message):
    """
    Обновление статуса Матвея.
    """
    global status
    if message.from_user.id == ADMIN_ID:
        if message.text == "Я в общаге":
            status = "Матвей в общаге"
        elif message.text == "Меня нет в общаге":
            status = "Матвея нет в общаге"
        await message.answer("Ваш статус обновлён.")
    else:
        await message.answer("Эта команда доступна только для Матвея.")


@dp.message(lambda message: message.text == "Узнать где Матвей")
async def get_status(message: types.Message):
    """
    Сообщение статуса другим пользователям.
    """
    global status
    if status == "неизвестен":
        await message.answer("Статус Матвея пока не обновлён.")
    else:
        await message.answer(status)


@dp.message(lambda message: message.text == "Связаться")
async def contact_admin(message: types.Message):
    """
    Выдача ссылки на Telegram-аккаунт администратора.
    """
    await message.answer(f"Вы можете связаться с Матвеем по этой ссылке: {ADMIN_USERNAME}")


@dp.message()
async def fallback(message: types.Message):
    """
    Обработчик всех других сообщений.
    """
    if message.from_user.id == ADMIN_ID:
        await message.answer("Используй кнопки для обновления статуса.", reply_markup=admin_kb)
    else:
        await message.answer("Нажмите кнопку, чтобы узнать, где Матвей, или связаться с ним.", reply_markup=user_kb)


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())