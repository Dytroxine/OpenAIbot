import gspread
from oauth2client.service_account import ServiceAccountCredentials
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN= os.getenv('BOT_TOKEN')

ADMIN_IDS = [os.getenv('ADMIN_IDS')]

SERVICE_ACCOUNT_FILE = "credentials.json"

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')



bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(credentials)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

last_notified_row = 0

async def check_sheet_changes():
    global last_notified_row

    while True:
        await asyncio.sleep(10)
        try:
            last_row = len(sheet.col_values(1))

            if last_row > last_notified_row:
                row_values = sheet.row_values(last_row)

                row_link = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid=0&range={last_row}:{last_row}"

                contact = row_values[0]
                category = row_values[1]
                information = row_values[2]
                notification = f"{category}\n\nКонтакт: `{contact}`\nИнформация: {information}\n\n[Ссылка на ячейку]({row_link})"

                for admin_id in ADMIN_IDS:
                    await bot.send_message(admin_id, notification, disable_web_page_preview=True, parse_mode='Markdown')

                last_notified_row = last_row

        except Exception as e:
            print("Ошибка при проверке таблицы Google Sheets:", e)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("Привет! Я буду уведомлять тебя о новых значениях на листе Google Sheets.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(check_sheet_changes())
    executor.start_polling(dp, skip_updates=True)
