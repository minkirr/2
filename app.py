7561870576:AAHSEpjx1nNH4aa6WBwNEe3MQzmWSsKUOCA

from telegram_token import TELEGRAM_TOKEN
import json
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.web_app import check_webapp_signature


bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(
            text="Открыть WebApp",
            web_app=types.WebAppInfo(url="https://minkirr.github.io/web2/")
        )
    ]])
    await message.answer("Тест WebApp:", reply_markup=kb)

@dp.message()
async def handle_all_messages(message: types.Message):
    print(f"\n{'='*40}\nПолучено сообщение:")
    print(f"Тип: {message.content_type}")
    print(f"Данные: {json.dumps(message.dict(), indent=2, ensure_ascii=False)}")


    if message.web_app_data:  # Проверяем наличие WebApp данных
        try:
            # Получаем сырые данные напрямую из message.web_app_data
            webapp_data = message.web_app_data.data
            print(f"WebApp данные (сырые): {webapp_data}")
            
            # Проверяем подпись (если нужно)
            init_data = message.web_app_data.web_app_init_data
            if init_data and not check_webapp_signature(TELEGRAM_TOKEN, init_data):
                await message.answer("❌ Ошибка: Невалидные данные WebApp")
                return
            
            # Парсим JSON данные
            parsed_data = json.loads(webapp_data)
            print(f"WebApp данные (парсированные): {parsed_data}")
            
            # Записываем в файл
            with open("received_data.txt", "a", encoding="utf-8") as f:
                f.write(f"{message.from_user.id}: {parsed_data}\n")
                
            await message.answer(f"✅ Получено через WebApp:\n{json.dumps(parsed_data, indent=2, ensure_ascii=False)}")
            
        except json.JSONDecodeError:
            await message.answer("❌ Ошибка: Невалидный JSON в данных WebApp")
        except Exception as e:
            logging.exception("Ошибка обработки WebApp данных")
            await message.answer(f"❌ Произошла ошибка: {str(e)}")
    else:
        print("Обычное сообщение")
        await message.answer(f"📨 Получено: {message.text}")

async def main():
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())