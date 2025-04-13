from aiogram import Bot, types, F
from aiogram.enums import ContentType, ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import json

# Шаг 1. Выбор типа подарочного сертификата
async def handle(bot: Bot, message: types.Message):
    builder = InlineKeyboardBuilder()
    options = [
        ("🎨 Интенсив", "gift_cert_intensive"),
        ("🎭 Мероприятие", "gift_cert_event"),
        ("💼 Коворкинг", "gift_cert_kovorking"),
        ("💌 Свидание", "gift_cert_date"),
        ("👩‍🏫 Индивидуальный курс", "gift_cert_individual")
    ]

    for text, callback_data in options:
        builder.add(types.InlineKeyboardButton(text=text, callback_data=callback_data))
    builder.adjust(1)

    await message.answer("Выберите тип подарочного сертификата:", reply_markup=builder.as_markup())

# Шаг 2. Показ кнопки WebApp после выбора
async def show_webapp_button_handler(callback: types.CallbackQuery):
    cert_type_map = {
        "gift_cert_intensive": "Интенсив",
        "gift_cert_event": "Мероприятие",
        "gift_cert_kovorking": "Коворкинг",
        "gift_cert_date": "Свидание",
        "gift_cert_individual": "Индивидуальный курс"
    }

    cert_type = cert_type_map.get(callback.data, "Неизвестный тип")
    webapp_keyboard = ReplyKeyboardBuilder()
    webapp_keyboard.add(
        types.KeyboardButton(
            text="🌐 Заполнить данные",
            web_app=types.WebAppInfo(url=f"https://strangepineaplle.github.io/lobzik-web/?cert_type={cert_type}")
        )
    )

    await callback.message.edit_reply_markup()
    await callback.message.answer(
        f"Вы выбрали сертификат: <b>{cert_type}</b>\nНажмите кнопку ниже и заполните форму:",
        parse_mode=ParseMode.HTML,
        reply_markup=webapp_keyboard.as_markup(resize_keyboard=True)
    )
    await callback.answer()

# Шаг 3. Получение и сохранение данных из WebApp
async def handle_webapp_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        file_path = "gift_certificates.json"

        record = {
            "tg_id": message.from_user.id,
            "tg_username": message.from_user.username or "",
            "full_name": data.get("full_name", ""),
            "user_phone": data.get("user_phone", ""),
            "user_email": data.get("user_email", ""),
            "cert_type": data.get("cert_type", "Неизвестно")
        }

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
                if not isinstance(existing, list):
                    existing = [existing]
        except (FileNotFoundError, json.JSONDecodeError):
            existing = []

        existing.append(record)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        await message.answer(
            f"🎁 Сертификат: <b>{record['cert_type']}</b>\n\n"
            f"👤 {record['full_name']}\n📞 {record['user_phone']}\n📧 {record['user_email']}",
            parse_mode=ParseMode.HTML
        )
        await message.answer("✅ Сертификат успешно сохранён!")
    except Exception as e:
        await message.answer(f"Ошибка при сохранении: {str(e)}")
