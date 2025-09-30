import gspread
import asyncio
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os

load_dotenv()

async def update_spreadsheet(user_id, info, has, data):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

    client = gspread.authorize(credentials)

    spreadsheet_id = os.getenv("spreadsheet_id")

    spreadsheet = client.open_by_key(spreadsheet_id)

    sheet = spreadsheet.sheet1

    sheet.append_row([user_id, info, has, data])

    spreadsheet_url = spreadsheet.url
    print('Ссылка на вашу таблицу:', spreadsheet_url)

    spreadsheet.share(None, perm_type='anyone', role='writer')
    print('Теперь ваша таблица доступна для редактирования всем, у кого есть ссылка.')

import gspread
from oauth2client.service_account import ServiceAccountCredentials

async def send_dialogue(values):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

    client = gspread.authorize(credentials)

    spreadsheet_id = os.getenv("spreadsheet_id")

    spreadsheet = client.open_by_key(spreadsheet_id)

    dialogue_sheet = spreadsheet.worksheet('Dialogue')

    last_row = len(dialogue_sheet.col_values(1)) + 1

    dialogue_sheet.insert_row(values, last_row)

async def add_values(user_id, value_1):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

    client = gspread.authorize(credentials)

    spreadsheet_id = os.getenv("spreadsheet_id")

    spreadsheet = client.open_by_key(spreadsheet_id)

    worksheet = spreadsheet.worksheet("integration")

    user_ids = worksheet.col_values(1)

    if user_id not in user_ids:
        values_to_insert = [user_id, value_1]
        worksheet.append_row(values_to_insert)


