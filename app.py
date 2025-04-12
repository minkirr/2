import logging
import json
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.enums import ContentType, ParseMode
from aiogram.filters import CommandStart
import nest_asyncio

logging.basicConfig(level=logging.INFO)

TOKEN = "7399282843:AAF85bKUZdZzHTbSSJOVt8dQFjpILv9UxIU"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Inline-кнопка для раскрытия клавиатуры
show_button_builder = InlineKeyboardBuilder()
show_button_builder.add(
    types.InlineKeyboardButton(
        text="🔄 Показать кнопку отправки",
        callback_data="show_webapp_button"
    )
)

# Клавиатура с WebApp
webapp_keyboard = ReplyKeyboardBuilder()
webapp_keyboard.add(
    types.KeyboardButton(
        text="🌐 Отправить данные",
        web_app=types.WebAppInfo(url="https://strangepineaplle.github.io/lobzik-web/")
    )
)

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Добро пожаловать! Нажмите кнопку ниже, чтобы получить кнопку для отправки данных:",
        reply_markup=show_button_builder.as_markup()
    )

@dp.callback_query(F.data == "show_webapp_button")
async def show_webapp_button_handler(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup()  # Убираем inline-кнопку
    await callback.message.answer(
        "Кнопка для отправки данных:",
        reply_markup=webapp_keyboard.as_markup(resize_keyboard=True)
    )
    await callback.answer()

@dp.message(F.content_type == ContentType.WEB_APP_DATA)
async def handle_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        formatted = f'📌 {data["title"]}\n\n📝 {data["desc"]}\n\n{data["text"]}'

        with open('data.txt', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        await message.answer(formatted, parse_mode=ParseMode.HTML)
        await message.answer("✅ Данные успешно сохранены!")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")

async def main():
    print("bot started")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    nest_asyncio.apply()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")