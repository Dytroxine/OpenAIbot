import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import openai
from openai import OpenAI
import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
import re
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('token2')
bot = Bot(token)
dp = Dispatcher(bot)

client = OpenAI(api_key=os.getenv('api_key'), organization=os.getenv('organization'))


ASSISTANT_ID = os.getenv('asst_id')

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Вы можете задать мне любой вопрос.")

thread = client.beta.threads.create()



@dp.message_handler(content_types=[types.ContentType.TEXT, types.ContentType.PHOTO])
async def handle_message(message: types.Message):
    photo = False
    if message.content_type == types.ContentType.PHOTO:
        photo = message.photo[-1]
        file_id = photo.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path

        image = await bot.download_file(file_path)

        with open("src/downloaded_image.jpg", "wb") as f:
            f.write(image.read())
        await message.answer('Фото принято')

        file_id = client.files.create(
            file=open("src/downloaded_image.jpg", "rb"),
            purpose="assistants"
        )
        photo = True
        print(file_id.id)

        if message.caption:
            user_message = message.caption
        else:
            user_message = None
    elif message.content_type == types.ContentType.TEXT:
        user_message = message.text
    else:
        user_message = None

    if user_message:

            if photo == True:
                thread_message = client.beta.threads.messages.create(
                    thread.id,
                    role="user",
                    content=[{"type": "image_file", "image_file": {"file_id": file_id.id}},{"type":"text","text":user_message}],

                )
            else:
                thread_message = client.beta.threads.messages.create(
                    thread.id,
                    role="user",
                    content=user_message,
                )

            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=ASSISTANT_ID
            )

            status = 1
            count = 0
            msg = await message.reply(f"Generating answer... Wait time: 0 sec ")
            while True:
                keep_retrieving_run = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )

                await asyncio.sleep(1)

                count += 1
                if count == 40:
                    status = 0
                    await message.answer('An error occurred :(')
                    break

                print(f"Run status: {keep_retrieving_run.status} " + str(count) + " sec")
                await bot.edit_message_text(f"Generating answer... Wait time: {count} sec ", chat_id=msg.chat.id, message_id=msg.message_id)

                if keep_retrieving_run.status == "completed":
                    break
                await asyncio.sleep(1)

            if status == 1:
                messages = client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                response_text = messages.data[0].content[0].text.value
                await message.answer(response_text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
