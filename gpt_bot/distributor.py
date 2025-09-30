from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
from openai import OpenAI
import re
import os
from gog_api import *
from dotenv import load_dotenv

load_dotenv()


token = os.getenv("token")
bot = Bot(token)
dp = Dispatcher(bot)
client = OpenAI(api_key=os.getenv("api_key"), organization=os.getenv("organization"))

user_threads = {}


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(text="Hello, I am a chatbot of Cryptomus company. Please feel free to ask your questions, and I will try to help! Please do not forget that this is the BETA version. In case of any issues, be sure to contact the support service at @cryptomussupport. Working hours are from 6 AM to 9 PM UTC +0.", parse_mode='HTML')



@dp.message_handler(content_types=['text'])
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    user_message = message.text
    data = message.date.strftime("%Y-%m-%d")
    user_name = f'@{str(message.from_user.username)}'
    if user_id not in user_threads:
        new_thread = client.beta.threads.create()
        user_threads[user_id] = {"thread_id": new_thread.id}
    else:
        thread_id = user_threads[user_id]["thread_id"]

    async def get_answer(asst_id, msg, await_time=None):

        active_runs = client.beta.threads.runs.list(thread_id=user_threads[user_id]["thread_id"])
        if any(run.status == "running" for run in active_runs):
            await message.answer("Please wait while the previous request is being processed.")
            return

        threed_message = client.beta.threads.messages.create(
            thread_id=user_threads[user_id]["thread_id"],
            role="user",
            content=user_message
        )
        if asst_id == None:
            asst_id = os.getenv("get_answer_asst_id")

        run = client.beta.threads.runs.create(
            thread_id=user_threads[user_id]["thread_id"],
            assistant_id= asst_id
        )


        status = 1
        if await_time is None:
            await_time = 0
        count = await_time

        while True:
            keep_retrieving_run = client.beta.threads.runs.retrieve(
                thread_id=user_threads[user_id]["thread_id"],
                run_id=run.id
            )

            await asyncio.sleep(1)

            count += 1
            if count == 40:
                status = 0
                await message.answer('An error occurred :(')
                break

            print(f"User: {user_id} Run status: {keep_retrieving_run.status} " + str(count) + " sec")
            await bot.edit_message_text(f"Generating answer... Wait time: {count} sec ", chat_id=msg.chat.id, message_id=msg.message_id)

            if keep_retrieving_run.status == "completed":

                break
            await asyncio.sleep(1)

        if status == 1:
            messages = client.beta.threads.messages.list(
                thread_id=user_threads[user_id]["thread_id"]
            )

            return count, re.sub(r'【.*?】', '', messages.data[0].content[0].text.value)
    msg = await message.reply(f"Generating answer... Wait time: 0 sec ")

    await_time, response_text = await get_answer(None, msg)

    if response_text == 'asst_check':
        asst_id = os.getenv("response_asst_id")
        await_time, response_text = await get_answer(asst_id, msg, await_time)


        info = 'Проблема с переводом'
        if response_text.startswith("send_google "):
            response_text = response_text[len("send_google "):].lstrip()
            words = response_text.split()
            if len(words) > 0 and len(words[0]) > 15 and ' ' not in words[0]:
                has = words[0]
                response_text = ' '.join(words[1:])
                await update_spreadsheet(user_name, info, has, data)
                values = [user_name, user_message, response_text, str(data)]
                await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
                await message.answer(response_text, disable_web_page_preview=True, parse_mode='HTML')
                await send_dialogue(values)

            else:
                values = [user_name, user_message, response_text, str(data)]
                await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
                await message.answer(response_text, disable_web_page_preview=True, parse_mode='HTML')
                await send_dialogue(values)
        else:
            values = [user_name, user_message, response_text, str(data)]
            await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
            await message.answer(response_text, disable_web_page_preview=True, parse_mode='HTML')
            await send_dialogue(values)

    elif response_text == 'asst_merchant':
        asst_id = os.getenv("asst_check_asst_id")
        await_time, response_text = await get_answer(asst_id, msg, await_time)
        values = [user_name, user_message, response_text, str(data)]
        await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
        await message.answer(response_text, disable_web_page_preview=True, parse_mode='HTML')
        await send_dialogue(values)
        info = 'Интересовался интеграцией'
        await add_values(user_name, info)
    elif response_text == 'asst_FAQ':
        asst_id = os.getenv("faq_asst_id")
        await_time, response_text = await get_answer(asst_id, msg, await_time)
        values = [user_name, user_message, response_text, str(data)]
        await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
        await message.answer(response_text, disable_web_page_preview=True, parse_mode='HTML')
        await send_dialogue(values)
    elif response_text == 'asst_boltun':
        asst_id = os.getenv("boltun_asst_id")
        await_time, response_text = await get_answer(asst_id, msg, await_time)
        values = [user_name, user_message, response_text, str(data)]
        await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
        await message.answer(response_text, disable_web_page_preview=True, parse_mode='HTML')
        await send_dialogue(values)
    else:
        values = [user_name, user_message, response_text, str(data)]
        await bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
        await message.answer(response_text, disable_web_page_preview=True, parse_mode='HTML')
        await send_dialogue(values)

if __name__ == '__main__':
    executor = dp.start_polling()
    asyncio.get_event_loop().run_until_complete(executor)
