import asyncio

import config
import logging
import requests
from bs4 import BeautifulSoup as BS
from database import Database
from aiogram import Bot, Dispatcher, executor, types
import schedule, time

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot)
# initialising database
db = Database('randomJoke.db')

# keyboard
keyboardMarkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
item1 = types.KeyboardButton("😂Рандомный анекдот")
item2 = types.KeyboardButton("ℹ️Моя статистика")
item3 = types.KeyboardButton("🤖О боте")
keyboardMarkup.add(item1).add(item2).add(item3)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)

    sticker = open('AnimatedSticker1.tgs', 'rb')
    await bot.send_message(message.chat.id, 'Привет, я отправляю рандомный анекдот каждый час!😜 Что бы я отправил '
                                            'тебе еще, нажми кнопку внизу!👇️                                     Если '
                                            'хочешь отписатся от ежечасовой '
                                            'рассылки, напиши /unsubscribe🔕',
                           reply_markup=keyboardMarkup)
    # await bot.send_message(message.chat.id, message.from_user.id)
    await bot.send_sticker(message.chat.id, sticker)


@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if not db.get_subscription(message.chat.id):
        db.update_subscription(message.chat.id, True)
        await bot.send_message(message.chat.id, "Вы успешно подписались!😜 Что бы отписатся, введите /unsubscribe")
    elif db.get_subscription(message.chat.id):
        await bot.send_message(message.chat.id, 'Вы уже подписаны!😅')


@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if not db.get_subscription(message.chat.id):
        await bot.send_message(message.chat.id, 'Вы уже отписаны!😅')
    elif db.get_subscription(message.chat.id):
        db.update_subscription(message.chat.id, False)
        await bot.send_message(message.chat.id,
                               "Вы успешно отписались.😟 Что бы подписатся обратно, введите /subscribe")


@dp.message_handler(content_types=['text'])
async def get_joke(message: types.message):
    if message.text == '😂Рандомный анекдот':
        await send_joke(message)
    elif message.text == "ℹ️Моя статистика":
        await bot.send_message(message.chat.id,
                               "Разница(Смешно - Не смешно) ➡️" + str(db.get_difference(message.from_user.id)))
        await bot.send_message(message.chat.id,
                               "Вы подписаны!😜" if db.get_subscription(message.from_user.id) else "Вы не подписаны.😟")
    elif message.text == "🤖О боте":
        await bot.send_message(message.chat.id, "Это тестовый бот, написаный для тренировки разработки телеграм-ботов."
                                                "Функционал: по запросу отправлять анекдот пользователю. Имеет "
                                                "возможность получить отзыв и фиксирует результат в БД. Рассылка "
                                                "анекдотов пользователям - каждый час, если оформлена подписка(при "
                                                "регистрации оформляется автоматически)."
                                                "Анегдоты парсятся с сервиса https://nekdo.ru/random плагином "
                                                "BeautifulSoup4. Данные пользователей хранятся в базе данных SQLite. "
                                                "А точнее: Telegram-ID пользователя, разница('Смешно' - 'Не смешно'), "
                                                "статус подписки пользователя.")


async def scheduled(wait_for, message: types.Message):
    while True:
        if db.get_subscription(message.from_user.id):
            await send_joke(message)


@dp.callback_query_handler(lambda c: c.data)
async def callback_inline(callback_query: types.CallbackQuery):
    if callback_query.data == "funny":
        if not db.user_exists(callback_query.from_user.id):
            db.add_user(callback_query.from_user.id)
        await bot.send_message(callback_query.message.chat.id, "Спасибо за ответ, я стараюсь!😊")

        db.update_difference(callback_query.from_user.id, int(db.get_difference(callback_query.from_user.id)) + 1)

    elif callback_query.data == "not_funny":
        if not db.user_exists(callback_query.from_user.id):
            db.add_user(callback_query.from_user.id)
        await bot.send_message(callback_query.message.chat.id, "Спасибо за ответ, извините.😢")
        db.update_difference(callback_query.from_user.id, int(db.get_difference(callback_query.from_user.id)) - 1)
    await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id,
                                text=callback_query.message.text, reply_markup=None)
    await bot.answer_callback_query(callback_query.id, show_alert=False, text="Это тестовое уведомление😊")


async def send_joke(message: types.message):
    inline_markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton("Смешно😂", callback_data='funny'),
                types.InlineKeyboardButton("Не смешно😕", callback_data='not_funny')
            ],
            [
                types.InlineKeyboardButton("Ещё анекдоты🔗", url="https://nekdo.ru/random")
            ]
        ]
    )

    r = requests.get("https://nekdo.ru/random")
    html = BS(r.content, 'html.parser')
    sticker = open('sticker1.webp', 'rb')
    await bot.send_message(message.chat.id, html.find("div", {"class": "text"}).text, reply_markup=inline_markup)


if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.create_task(scheduled(10))
    executor.start_polling(dp, skip_updates=True)
