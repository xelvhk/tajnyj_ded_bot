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
    await message.answer(f"Здравствуй, {message.from_user.full_name}! ты участвуешь в Тайном Санте! Вот только у нас не Санта, а Дед! Дед Мороз! Жди, пока подойдут остальные коллеги")


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
    router.message.register(save_gift_message)

# Обработчик для сохранения сообщения о подарке
async def save_gift_message(message: Message):
    user_id = message.from_user.id
    gift_message = message.text
    cursor.execute("UPDATE users SET gift_message = ? WHERE user_id = ?", (gift_message, user_id))
    conn.commit()
    await message.reply("Сообщение о подарке сохранено!")

# Обработчик для отображения подарков
@router.message(F.text.in_([LEXICON_RU['gifts']]))
async def show_gifts(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT gift_message, santa_for FROM users WHERE user_id = ?", (user_id,))
    gift_message, santa_for_id = cursor.fetchone()

    # Проверка наличия данных
    if not gift_message:
        gift_message = "Вы еще не указали, что хотите получить в подарок."

    if santa_for_id:
        cursor.execute("SELECT username, gift_message FROM users WHERE id = ?", (santa_for_id,))
        gift_for_user = cursor.fetchone()
        if gift_for_user:
            recipient_username, recipient_gift_message = gift_for_user
            recipient_gift_message = recipient_gift_message or "не указал, что хочет получить в подарок."
            await message.answer(
                f"Привет, {message.from_user.full_name}!\n\n"
                f"Вы хотите получить: {gift_message}\n\n"
                f"Вы дарите подарок для @{recipient_username}, и он(а) хочет: {recipient_gift_message}"
            )
        else:
            await message.answer(f"Не удалось найти пользователя, которому вы дарите подарок.")
    else:
        await message.answer("Вы еще не были назначены тайным дедом для кого-либо.")

# Обработчик для кнопки "Как бросить снежок?"
@router.message(F.text.in_([LEXICON_RU['how_snowball']]))
async def how_snowball(message: Message):
    await message.answer(text=LEXICON_RU['snow'])

# Обработчик команды "Бросить снежок"
@router.message(lambda message: message.text.lower().startswith("бросить снежок в"))
async def throw_snowball(message: Message):
    # Извлекаем ID или username цели из сообщения
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.reply("Пожалуйста, укажите ID или username цели после 'бросить снежок в'.")
        return
    
    target = parts[3]  # ID или username цели
    user_id = message.from_user.id

    # Проверяем, существует ли пользователь с таким ID или username
    cursor.execute("SELECT id, username FROM users WHERE id = ? OR username = ?", (target, target))
    result = cursor.fetchone()
    
    if result:
        target_id, target_username = result
        # Увеличиваем счетчик попаданий и обновляем список бросавших
        cursor.execute("UPDATE users SET snowball_hits = snowball_hits + 1 WHERE id = ?", (target_id,))
        cursor.execute("SELECT throwers FROM users WHERE id = ?", (target_id,))
        throwers = cursor.fetchone()[0] or ""
        throwers = f"{throwers}, {message.from_user.username}" if throwers else message.from_user.username
        cursor.execute("UPDATE users SET throwers = ? WHERE id = ?", (throwers, target_id))
        conn.commit()
        await message.reply(f"Снежок брошен в @{target_username}, {message.from_user.full_name}!")
    else:
        await message.reply("Пользователь не найден. Укажите корректный ID или username.")

# Обработчик для "В меня попали"
@router.message(F.text.in_([LEXICON_RU['hit']]))
async def show_hits(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT snowball_hits, throwers FROM users WHERE user_id = ?", (user_id,))
    hits, throwers = cursor.fetchone()
    throwers_list = throwers.split(", ") if throwers else []
    throwers_text = "\n".join([f"@{thrower}" for thrower in throwers_list]) if throwers_list else "никто не бросал"
    await message.answer(
        f"{message.from_user.full_name}, в вас попали {hits} раз(а).\n"
        f"Бросали снежки:\n{throwers_text}"
    )