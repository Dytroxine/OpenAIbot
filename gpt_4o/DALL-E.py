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

TELEGRAM_TOKEN = os.getenv('tg_token')
client = OpenAI(api_key=os.getenv('api_key'), organization=os.getenv('organization'))


bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь мне текст, и я сгенерирую изображение с помощью DALL-E.")

@dp.message_handler()
async def generate_image(message: types.Message):
    user_message = message.text
    response = client.images.generate(
        model="dall-e-3",
        prompt=user_message,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    await message.reply_photo(photo=image_url, caption="Вот ваше изображение, сгенерированное DALL-E.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
