from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ContentType
from database import Database
import cfg as c
import joblib
import nltk
import pymorphy3
import regex as re

stopw = nltk.corpus.stopwords.words('russian')
morph = pymorphy3.MorphAnalyzer()
reg = re.compile(r'[а-яё]+')
chat_id = c.chat_id
storage = MemoryStorage()
TOKEN = c.TOKEN
bot = Bot(token=c.TOKEN)
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
MyDataB = Database(password="Tetsuya", dbname="chat_bot")


def tokenize(sentence: str) -> list[str]:
    sentence = sentence.lower().strip()
    sentence = reg.findall(sentence)
    return [token for token in sentence if len(token)]


def morph_stopper(list_of_tokens: list[str]) -> list[str]:
    return [morph.parse(word)[0].normal_form for word in list_of_tokens if len(word) > 2]


def stop_words(list_of_morphs: list[str]) -> list[str]:
    return [word for word in list_of_morphs if word not in stopw]


def cleaner(sentence: str) -> str:
    mtoke = stop_words(morph_stopper(tokenize(sentence)))
    print(mtoke)
    return " ".join(mtoke)


def ans(text: str) -> bool:
    model = joblib.load("final_model.joblib")
    trash_talk = 0.86
    proba = model.predict_proba([text])[:, 1]
    return True if proba >= trash_talk else False


@dp.message_handler(lambda message: message.chat.type == "private", commands=["start"])
async def aboba(message: types.Message):
    await bot.send_message(message.from_id, "Ссылка на чатик https://t.me/+R_5nFR2ZX58xN2Zi")


@dp.message_handler(lambda message: message.chat.type == "private", commands=["clear"])
async def cl(message: types.Message):
    MyDataB.clear_values("comment")


@dp.message_handler(lambda message: message.chat.type == "private",
                    content_types=ContentType.TEXT)
async def reply_to_all_messages(message: types.Message):
    await message.reply("I received your message!")


@dp.message_handler(lambda message: message.is_automatic_forward, content_types=types.ContentType.TEXT)
async def handle_channel_posts(message: types.Message):
    await message.reply("Следите за тем, что вы пишите в комментариях")


@dp.message_handler(content_types=types.ContentType.TEXT, chat_type=types.ChatType.SUPERGROUP)
async def handle_group_comments(message: types.Message):
    is_violent = ans(message.text)
    MyDataB.add_values('comment', comment=message.text, user_id=message.from_id, is_violent=is_violent)
    print(MyDataB.get_values("comment"))
    if is_violent:
        await bot.send_message(message.from_id, f"Комментарии типа - '{message.text}' Недопустимы в нашем чате")
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
