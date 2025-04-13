from aiogram import Bot, types, F
from aiogram.enums import ContentType, ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import json
import os

# Хендлер по кнопке "интенсив"
async def handle(bot: Bot, message: types.Message):
    show_button_builder = InlineKeyboardBuilder()
    show_button_builder.add(
        types.InlineKeyboardButton(
            text="🔄 Показать кнопку отправки",
            callback_data="show_intense_webapp_button"
        )
    )

    await message.answer(
        "Чтобы записаться на интенсив, нажми на кнопку ниже 👇",
        reply_markup=show_button_builder.as_markup()
    )

# Callback: показать WebApp-кнопку
async def show_webapp_button_handler(callback: types.CallbackQuery):
    webapp_keyboard = ReplyKeyboardBuilder()
    webapp_keyboard.add(
        types.KeyboardButton(
            text="🌐 Отправить данные",
            web_app=types.WebAppInfo(url="https://strangepineaplle.github.io/lobzik-web/")
        )
    )

    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "Кнопка для отправки данных:",
        reply_markup=webapp_keyboard.as_markup(resize_keyboard=True)
    )
    await callback.answer()

# Обработка данных из WebApp и сохранение в database.json
async def handle_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)

        entry = {
            "tg_id": message.from_user.id,
            "tg_username": message.from_user.username,
            "full_name": data.get("full_name"),
            "user_phone": data.get("phone"),
            "user_email": data.get("email"),
            "category": "интенсив"
        }

        file_path = "database.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        existing_data.append(entry)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

        formatted = (
            f'📌 <b>{entry["category"]}</b>\n\n'
            f'👤 ФИО: {entry["full_name"]}\n'
            f'📞 Телефон: {entry["user_phone"]}\n'
            f'📧 Email: {entry["user_email"]}'
        )

        await message.answer(formatted, parse_mode=ParseMode.HTML)
        await message.answer("✅ Данные успешно сохранены!")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")