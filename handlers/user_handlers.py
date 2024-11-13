from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from keyboards.keyboards import yaded_kb
from lexicon.lexicon_ru import LEXICON_RU
from services.services import start_record
import sqlite3
import random

router = Router()
bot = Bot
conn = sqlite3.connect('data/santas.db')
cursor = conn.cursor()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    start_record()
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    await message.answer(text=LEXICON_RU['/start'],
                         reply_markup=yaded_kb)
    await message.answer(f"Здравствуй, {message.from_user.full_name}! ты участвуешь в Тайном Санте! Жди, пока подойдут остальные коллеги")


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])

# Обработчик для "Стать тайным дедом"
@router.message(F.text.in_([LEXICON_RU['yaded']]))
async def become_santa(message: Message):
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    user_id = message.from_user.id

    if count < 14:
        await message.reply(f"{message.from_user.full_name}, пожалуйста, подожди, пока наберется 14 участников.")
        return

    cursor.execute("SELECT santa_for FROM users WHERE user_id = ?", (user_id,))
    santa_for = cursor.fetchone()[0]
    if santa_for is not None:
        cursor.execute("SELECT username FROM users WHERE id = ?", (santa_for,))
        gift_for = cursor.fetchone()[0]
        await message.answer(f"{message.from_user.full_name},ты тайный Санта для @{gift_for}!")
    else:
        cursor.execute("SELECT user_id FROM users WHERE santa_for IS NULL")
        user_ids = [row[0] for row in cursor.fetchall()]
        random.shuffle(user_ids)

        for i, user in enumerate(user_ids):
            santa_for = user_ids[(i + 1) % len(user_ids)]
            cursor.execute("UPDATE users SET santa_for = ? WHERE user_id = ?", (santa_for, user))
        conn.commit()
        cursor.execute("SELECT santa_for FROM users WHERE user_id = ?", (user_id,))
        santa_for_id = cursor.fetchone()[0]
        cursor.execute("SELECT username FROM users WHERE user_id = ?", (santa_for_id,))
        gift_for = cursor.fetchone()[0]
        
        await message.answer(f"{message.from_user.full_name}, ты теперь тайный Санта для @{gift_for}!")
    await message.answer("\n Напиши пока что хочешь в подарок:")
    router.message.register(save_gift_message, user_id=user_id)

# Обработчик для сохранения сообщения о подарке
async def save_gift_message(message: Message):
    user_id = message.from_user.id
    gift_message = message.text
    cursor.execute("UPDATE users SET gift_message = ? WHERE user_id = ?", (gift_message, user_id))
    conn.commit()
    await message.reply("Сообщение о подарке сохранено!")

# Обработчик для "Бросить снежок"
@router.message(F.text.in_([LEXICON_RU['snowball']]))
async def throw_snowball(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT id FROM users WHERE user_id != ?", (user_id,))
    ids = [row[0] for row in cursor.fetchall()]
    
    if ids:
        await message.answer("Укажи ID пользователя, в которого хочешь бросить снежок:")
        router.message.register(handle_snowball_throw, ids=ids)

async def handle_snowball_throw(message: Message, ids):
    try:
        target_id = int(message.text)
        if target_id in ids:
            cursor.execute("UPDATE users SET snowball_hits = snowball_hits + 1 WHERE id = ?", (target_id,))
            cursor.execute("SELECT throwers FROM users WHERE id = ?", (target_id,))
            throwers = cursor.fetchone()[0]
            throwers = f"{throwers}, {message.from_user.username}" if throwers else message.from_user.username
            cursor.execute("UPDATE users SET throwers = ? WHERE id = ?", (throwers, target_id))
            conn.commit()
            await message.reply("Снежок брошен!")
        else:
            await message.reply("Некорректный ID. Попробуй еще раз.")
    except ValueError:
        await message.reply(f"{message.from_user.full_name}, пожалуйста, укажи число.")

# Обработчик для "В меня попали"
@router.message(F.text.in_([LEXICON_RU['hit']]))
async def show_hits(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT snowball_hits, throwers FROM users WHERE user_id = ?", (user_id,))
    hits, throwers = cursor.fetchone()
    await message.answer(f"{message.from_user.full_name}, в тебя попали {hits} раз(а). Бросали снежки: {throwers or 'никто не бросал'}.")