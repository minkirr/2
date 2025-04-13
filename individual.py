from aiogram import Bot, types, F
from aiogram.enums import ContentType, ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import json
import os

# Хендлер по кнопке "Индивидуальный курс"
async def handle(bot: Bot, message: types.Message):
    show_button_builder = InlineKeyboardBuilder()
    show_button_builder.add(
        types.InlineKeyboardButton(
            text="🔄 Показать кнопку отправки",
            callback_data="show_individual_webapp_button"
        )
    )

    await message.answer(
        "Чтобы записаться на индивидуальный курс, нажми на кнопку ниже 👇",
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

        # Собираем данные из message и из формы WebApp
        user_data = {
            "tg_id": message.from_user.id,
            "tg_username": message.from_user.username,
            "full_name": data.get("full_name", "Не указано"),  # Используем данные из формы
            "user_phone": data.get("phone", ""),
            "user_email": data.get("email", "")
        }

        # Путь к файлу
        file_path = "database.json"
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        # Добавляем новый объект
        existing_data.append(user_data)

        # Сохраняем в файл
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

        formatted = (
            f'📌 <b>{data.get("full_name", "Без имени")}</b>\n\n'
            f'📱 Телефон: {data.get("phone", "не указан")}\n'
            f'📧 Email: {data.get("email", "не указан")}'
        )

        await message.answer(formatted, parse_mode=ParseMode.HTML)
        await message.answer("✅ Данные индивидуального курса сохранены!")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
