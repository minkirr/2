#7561870576:AAHSEpjx1nNH4aa6WBwNEe3MQzmWSsKUOCA
#https://minkirr.github.io/web2/


from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from telegram_token import TELEGRAM_TOKEN


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем кнопку с Mini App
    keyboard = [
        [InlineKeyboardButton(
            "🕒 Установить время",
            web_app=WebAppInfo(url="https://мой-личный-диетолог.рф/time-widget/test.html?time=9:33")
        )]
    ]

    await update.message.reply_text(
        "Нажмите кнопку чтобы установить время:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем данные из Mini App
    data = update.message.web_app_data.data
    await update.message.reply_text(f"Получены данные: {data}")


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