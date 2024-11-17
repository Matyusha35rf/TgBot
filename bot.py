import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID, ADMIN_USERNAME

# Инициализация бота, диспетчера и хранилища состояний
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Файл для хранения каталога
CATALOG_FILE = "catalog.json"

# Переменная для хранения статуса
status = "неизвестно"

# Определение клавиатур
admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Изменить статус")],
        [KeyboardButton(text="Добавить товар"), KeyboardButton(text="Удалить товар")],
        [KeyboardButton(text="Просмотреть каталог")]
    ],
    resize_keyboard=True
)

user_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Когда можно забрать товар?")],
        [KeyboardButton(text="Каталог"), KeyboardButton(text="Связаться")]
    ],
    resize_keyboard=True
)


# Состояния для управления товарами
class ProductState(StatesGroup):
    waiting_for_name = State()
    waiting_for_number = State()
    waiting_for_status_update = State()


def load_catalog():
    """
    Загружает каталог из файла. Если файл отсутствует, возвращает пустой список.
    """
    try:
        with open(CATALOG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_catalog(catalog):
    """
    Сохраняет каталог в файл.
    """
    with open(CATALOG_FILE, "w", encoding="utf-8") as file:
        json.dump(catalog, file, ensure_ascii=False, indent=4)


# Инициализация каталога
catalog = load_catalog()


@dp.message(Command("start"))
async def start_handler(message: types.Message):
    """
    Обработчик команды /start.
    """
    if message.from_user.id == ADMIN_ID:
        await message.answer("Привет, Матвей! Используй кнопки для управления.", reply_markup=admin_kb)
    else:
        await message.answer("Привет!\nНажмите кнопку, чтобы узнать, когда можно забрать товар,\
                              просмотреть каталог или связаться с ним.", reply_markup=user_kb)


@dp.message(lambda message: message.text in ["Изменить статус"])
async def status_update(message: types.Message, state: FSMContext):
    """
    Обновление статуса Матвея.
    """
    global status
    if message.from_user.id == ADMIN_ID:
        await message.answer("Введите статус!")
        await state.set_state(ProductState.waiting_for_status_update)
    else:
        await message.answer("Эта команда доступна только для Матвея.")

@dp.message(ProductState.waiting_for_status_update) 
async def status_update(message: types.Message, state: FSMContext):
    global status
    status = message.text
    await message.answer("Статус обновлён!")
    

@dp.message(lambda message: message.text == "Когда можно забрать товар?")
async def get_status(message: types.Message):
    """
    Сообщение статуса другим пользователям.
    """
    global status
    await message.answer(status)


@dp.message(lambda message: message.text == "Связаться")
async def contact_admin(message: types.Message):
    """
    Выдача ссылки на Telegram-аккаунт администратора.
    """
    contact_link = f"https://t.me/{ADMIN_USERNAME}"
    await message.answer(f"Вы можете связаться с Матвеем по этой ссылке: {contact_link}")


@dp.message(lambda message: message.text == "Добавить товар")
async def add_product(message: types.Message, state: FSMContext):
    """
    Добавление товара в каталог (только для администратора).
    """
    if message.from_user.id == ADMIN_ID:
        await message.answer("Введите название товара, чтобы добавить его в каталог.")
        await state.set_state(ProductState.waiting_for_name)
    else:
        await message.answer("Эта команда доступна только администратору.")


@dp.message(ProductState.waiting_for_name)
async def add_product_name(message: types.Message, state: FSMContext):
    """
    Обработчик ввода названия товара.
    """
    catalog.append(message.text)
    save_catalog(catalog)
    await message.answer(f"Товар \"{message.text}\" добавлен в каталог.", reply_markup=admin_kb)
    await state.clear()


@dp.message(lambda message: message.text == "Удалить товар")
async def remove_product(message: types.Message, state: FSMContext):
    """
    Удаление товара из каталога (только для администратора).
    """
    if message.from_user.id == ADMIN_ID:
        if not catalog:
            await message.answer("Каталог пуст, нечего удалять.")
        else:
            catalog_list = "\n".join([f"{i+1}. {item}" for i, item in enumerate(catalog)])
            await message.answer(f"Каталог:\n{catalog_list}\n\nВведите номер товара, который хотите удалить.")
            await state.set_state(ProductState.waiting_for_number)
    else:
        await message.answer("Эта команда доступна только администратору.")


@dp.message(ProductState.waiting_for_number)
async def remove_product_by_number(message: types.Message, state: FSMContext):
    """
    Обработчик ввода номера товара для удаления.
    """
    try:
        index = int(message.text) - 1
        if 0 <= index < len(catalog):
            removed_item = catalog.pop(index)
            save_catalog(catalog)
            await message.answer(f"Товар \"{removed_item}\" удалён из каталога.", reply_markup=admin_kb)
        else:
            await message.answer("Некорректный номер. Попробуйте ещё раз.")
    except ValueError:
        await message.answer("Пожалуйста, введите номер.")
    await state.clear()


@dp.message(lambda message: message.text == "Просмотреть каталог")
async def view_catalog_admin(message: types.Message):
    """
    Просмотр каталога товаров (администратор).
    """
    if catalog:
        catalog_list = "\n".join([f"{i+1}. {item}" for i, item in enumerate(catalog)])
        await message.answer(f"Каталог:\n{catalog_list}")
    else:
        await message.answer("Каталог пуст.")


@dp.message(lambda message: message.text == "Каталог")
async def view_catalog_user(message: types.Message):
    """
    Просмотр каталога товаров (пользователь).
    """
    if catalog:
        catalog_list = "\n".join([f"{i+1}. {item}" for i, item in enumerate(catalog)])
        await message.answer(f"Каталог:\n{catalog_list}")
    else:
        await message.answer("Каталог пуст.")


@dp.message()
async def fallback(message: types.Message):
    """
    Обработчик всех других сообщений.
    """
    if message.from_user.id == ADMIN_ID:
        await message.answer("Используй кнопки для управления.", reply_markup=admin_kb)
    else:
        await message.answer("Нажмите кнопку, чтобы узнать, где Матвей, просмотреть каталог или связаться с ним.", reply_markup=user_kb)


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())