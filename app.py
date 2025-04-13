import logging
import json
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.enums import ContentType, ParseMode
from aiogram.filters import CommandStart

logging.basicConfig(level=logging.INFO)

TOKEN = "7561870576:AAHSEpjx1nNH4aa6WBwNEe3MQzmWSsKUOCA"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Импорты для обработчиков (добавьте свои модули)
import individual
import gift
import intense
import event
import kovorking

@dp.message(CommandStart())
async def start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    buttons = [
        "Индивидуальный курс",
        "подарить сертификат",
        "интенсив",
        "мероприятие",
        "коворкинг"
    ]
    
    for button in buttons:
        builder.add(types.KeyboardButton(text=button))
    builder.adjust(1)
    
    await message.answer(
        "Я бот лобзика бла бла помогу выбрать бла бла что вас интересует?",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

@dp.message(F.text == "Индивидуальный курс")
async def handle_individual_course(message: types.Message):
    await individual.handle(bot, message) 

dp.callback_query.register(individual.show_webapp_button_handler, F.data == "show_individual_webapp_button")
dp.message.register(individual.handle_webapp_data, F.content_type == ContentType.WEB_APP_DATA)


@dp.message(F.text == "подарить сертификат")
async def handle_gift_certificate(message: types.Message):
    await gift.handle(bot, message)

dp.callback_query.register(gift.show_webapp_button_handler, F.data.startswith("gift_cert_"))
dp.message.register(gift.handle_webapp_data, F.content_type == ContentType.WEB_APP_DATA)


@dp.message(F.text == "интенсив")
async def handle_intensive(message: types.Message):
    await intense.handle(bot, message)

@dp.message(F.text == "мероприятие")
async def handle_event(message: types.Message):
    await event.handle(bot, message)

@dp.message(F.text == "коворкинг")
async def handle_coworking(message: types.Message):
    await kovorking.handle(bot, message)



async def main():
    logging.info("Bot started")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped")





'''# Inline-кнопка для раскрытия клавиатуры
show_button_builder = InlineKeyboardBuilder()
show_button_builder.add(
    types.InlineKeyboardButton(
        text="🔄 Показать кнопку отправки",
        callback_data="show_webapp_button"
    )
)



reply_markup=show_button_builder.as_markup()




# Клавиатура с WebApp
webapp_keyboard = ReplyKeyboardBuilder()
webapp_keyboard.add(
    types.KeyboardButton(
        text="🌐 Отправить данные",
        web_app=types.WebAppInfo(url="https://strangepineaplle.github.io/lobzik-web/")
    )
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
        await message.answer(f"Ошибка: {str(e)}")'''
