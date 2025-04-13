from aiogram import Bot, types, F
from aiogram.enums import ContentType, ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import json

async def handle(bot: Bot, message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.add(
        types.InlineKeyboardButton(
            text="🔄 Показать кнопку отправки",
            callback_data="show_kovorking_webapp_button"
        )
    )
    await message.answer(
        "Чтобы записаться на коворкинг, нажми на кнопку ниже 👇",
        reply_markup=builder.as_markup()
    )

async def show_webapp_button_handler(callback: types.CallbackQuery):
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        types.KeyboardButton(
            text="🌐 Отправить данные",
            web_app=types.WebAppInfo(url="https://strangepineaplle.github.io/lobzik-web/")
        )
    )
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "Кнопка для отправки данных:",
        reply_markup=keyboard.as_markup(resize_keyboard=True)
    )
    await callback.answer()

async def handle_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        entry = {
            "tg_id": message.from_user.id,
            "tg_username": message.from_user.username,
            "full_name": data.get("full_name"),
            "user_phone": data.get("user_phone"),
            "user_email": data.get("user_email"),
            "category": "коворкинг"
        }

        file_path = "database.json"
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                db = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            db = []

        db.append(entry)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

        formatted = (
            f"<b>Коворкинг</b>\n\n"
            f"👤 {entry['full_name']}\n📞 {entry['user_phone']}\n📧 {entry['user_email']}"
        )

        await message.answer(formatted, parse_mode=ParseMode.HTML)
        await message.answer("✅ Заявка на коворкинг отправлена!")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")
