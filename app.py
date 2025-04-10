#7561870576:AAHSEpjx1nNH4aa6WBwNEe3MQzmWSsKUOCA
#https://minkirr.github.io/web2/


import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram_token import TELEGRAM_TOKEN
from pathlib import Path

DB_PATH = Path("database.json")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем кнопку с Mini App
    keyboard = [
        [InlineKeyboardButton(
            "🕒 Установить время",
            web_app=WebAppInfo(url="https://minkirr.github.io/web2/")
        )]
    ]

    await update.message.reply_text(
        "Нажмите кнопку, чтобы установить время:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def save_user_data_to_db(user_id: int, tg_username: str, full_name: str, user_phone: str, user_email: str):
    # Чтение существующего файла или создание нового
    if DB_PATH.exists():
        with DB_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    # Сохраняем данные пользователя по user_id
    data[str(user_id)] = {
        "tg_username": tg_username,
        "full_name": full_name,
        "user_phone": user_phone,
        "user_email": user_email
    }

    # Запись данных обратно в файл
    with DB_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем данные из WebApp
    data = update.message.web_app_data.data
    print(f"Получены данные: {data}")  # Логируем для отладки

    user_id = update.effective_user.id  # Получаем ID пользователя

    if data.startswith("time:"):
        time_value = data.split("time:")[1]
        # Сохраняем время в базу
        save_time_to_db(user_id, time_value)
        await update.message.reply_text(f"Время сохранено: {time_value}")

    elif data.startswith("user_data:"):
        # Парсим данные пользователя
        user_data = data.split("user_data:")[1]
        user_data_json = json.loads(user_data)

        full_name = user_data_json.get('full_name')
        user_phone = user_data_json.get('user_phone')
        user_email = user_data_json.get('user_email')
        tg_username = update.effective_user.username  # Получаем username Telegram

        # Сохраняем данные пользователя в базу
        save_user_data_to_db(user_id, tg_username, full_name, user_phone, user_email)

        await update.message.reply_text(f"Данные сохранены: {full_name}, {user_phone}, {user_email}")

    else:
        await update.message.reply_text("Неверный формат данных.")


def save_time_to_db(user_id: int, time: str):
    # Чтение существующего файла или создание нового
    if DB_PATH.exists():
        with DB_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    # Сохраняем время по user_id
    data[str(user_id)] = {"time": time}

    # Запись данных обратно в файл
    with DB_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    # Инициализация бота
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))

    # Запуск бота
    application.run_polling()


if __name__ == "__main__":
    main()
