import asyncio
import logging
import json
import urllib.parse
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

# --- НАСТРОЙКИ ---
TOKEN = "8520513948:AAEV8sx7FsTyTwAxeGnx205TUTeAuELDW0g"  # ЗАМЕНИ НА НОВЫЙ!
GROUP_ID = -5014567127
# Ссылка на твой index.html (когда зальешь на GitHub)
APP_URL = "https://твой-ник.github.io/vape-shop/"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Order(StatesGroup):
    phone = State()
    address = State()


# --- КЛАВИАТУРА С MINI APP ---
def main_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Открыть магазин", web_app=WebAppInfo(url=APP_URL))],
        [InlineKeyboardButton(text="💬 Оператор", url="https://t.me/your_username")]
    ])
    return kb


@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("Добро пожаловать! Нажми на кнопку ниже, чтобы открыть каталог:", reply_markup=main_menu())


# --- ПОЛУЧЕНИЕ ДАННЫХ ИЗ MINI APP ---
@dp.message(F.web_app_data)
async def web_app_receive(m: types.Message, state: FSMContext):
    data = json.loads(m.web_app_data.data)
    product = data.get("product")
    price = data.get("amount")

    await state.update_data(product=product, price=price)
    await state.set_state(Order.phone)
    await m.answer(f"Вы выбрали: {product} ({price} ₸)\n\nВведите ваш номер телефона:")


@dp.message(Order.phone)
async def get_phone(m: types.Message, state: FSMContext):
    await state.update_data(phone=m.text)
    await state.set_state(Order.address)
    await m.answer("📍 Введите адрес доставки:")


@dp.message(Order.address)
async def get_address(m: types.Message, state: FSMContext):
    data = await state.get_data()
    address = m.text

    # Генерация ссылки для Яндекс Такси (Курьер)
    encoded_addr = urllib.parse.quote(address)
    yandex_link = f"https://3.redirect.appmetrica.yandex.com/route?end-address={encoded_addr}&appmetrica_tracking_id=1178268795219780156"

    order_msg = (
        f"🆕 НОВЫЙ ЗАКАЗ\n\n"
        f"📦 Товар: {data['product']}\n"
        f"💰 Цена: {data['price']} ₸\n"
        f"📞 Тел: {data['phone']}\n"
        f"📍 Адрес: {address}"
    )

    # Кнопка для тебя (админа)
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚕 Вызвать Яндекс", url=yandex_link)]
    ])

    await bot.send_message(GROUP_ID, order_msg, reply_markup=admin_kb)
    await m.answer("✅ Заказ принят! Ожидайте звонка курьера.")
    await state.clear()


async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())