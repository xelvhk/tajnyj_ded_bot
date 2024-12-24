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
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.full_name
    start_record()
    # Добавляем пользователя в базу, если его там нет
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        await message.reply(
            f"Привет, {username}! \n \nЗа окном идёт снег, а у календаря остался последний листок? Значит скоро новый год... \n \nПришло время стать тайным дедом \nНапиши, что хочешь получить в подарок🧚‍♀️ Стоимость подарка до 1000 рублей.  \nЕсли не знаешь - напиши 'Хочу сюрприз' \nЭТО ОБЯЗАТЕЛЬНО!", 
            reply_markup=yaded_kb
        )
    else:
        await message.reply("Ты уже зарегистрирован. Напиши, что хочешь получить в подарок.", reply_markup=yaded_kb)



# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])

# Обработчик для "Стать тайным дедом"
@router.message(lambda message: message.text != LEXICON_RU['gifts'] and message.text != LEXICON_RU['yaded'])
async def save_gift(message: Message):
    user_id = message.from_user.id
    gift = message.text

    # Сохраняем подарок
    cursor.execute("UPDATE users SET gift = ? WHERE user_id = ?", (gift, user_id))
    conn.commit()
    await message.reply("Твой подарок сохранен! Теперь можно нажать на кнопку 'Стать тайным дедом' и стать тайным дедом")

    # Проверяем, набралось ли 13 участников
    cursor.execute("SELECT COUNT(*) FROM users WHERE gift IS NOT NULL")
    user_count = cursor.fetchone()[0]

    if user_count == 13:
        await distribute_santas()

@router.message(F.text.in_([LEXICON_RU['yaded']]))
async def become_santa(message: Message):
    user_id = message.from_user.id

    # Проверяем, набралось ли 13 участников
    cursor.execute("SELECT COUNT(*) FROM users WHERE gift IS NOT NULL")
    user_count = cursor.fetchone()[0]

    if user_count < 13:
        await message.reply(f"По айпи тебя вычислили, подожди, сейчас только {user_count} человек подключилось, скоро выберем кому подаришь 🎁. Попробуй нажать ещё раз чуть позже")
    else:
        # Показываем, кому пользователь дарит
        cursor.execute("SELECT santa_for FROM users WHERE user_id = ?", (user_id,))
        santa_for_id = cursor.fetchone()[0]

        if santa_for_id:
            cursor.execute("SELECT username, gift FROM users WHERE user_id = ?", (santa_for_id,))
            recipient_username, recipient_gift = cursor.fetchone()
            await message.answer(f"Пришло время дарить подарок @{recipient_username}. Этот человек хочет: {recipient_gift}")
        else:
            await message.answer("Произошла ошибка. Попробуйте позже.")

@router.message(F.text.in_([LEXICON_RU['gifts']]))
async def check_gifts(message: Message):
    user_id = message.from_user.id

    # Получаем свой подарок
    cursor.execute("SELECT gift FROM users WHERE user_id = ?", (user_id,))
    my_gift = cursor.fetchone()

    if not my_gift or not my_gift[0]:
        await message.answer("Ты еще не указал, что хочешь получить.")
        return

    my_gift = my_gift[0]

    # Проверяем, есть ли назначенный получатель
    cursor.execute("SELECT santa_for FROM users WHERE user_id = ?", (user_id,))
    santa_for_id = cursor.fetchone()[0]

    if not santa_for_id:
        await message.answer(f"Твой подарок: {my_gift}\nРаспределение еще не завершено, ожидаем всех участников.")
    else:
        cursor.execute("SELECT username, gift FROM users WHERE user_id = ?", (santa_for_id,))
        recipient_username, recipient_gift = cursor.fetchone()
        await message.answer(
            f"Твой подарок: {my_gift}\nТы даришь подарок @{recipient_username}. Этот человек хочет: {recipient_gift}"
        )

async def distribute_santas():
    # Получаем всех пользователей, которые указали подарки
    cursor.execute("SELECT user_id FROM users WHERE gift IS NOT NULL")
    user_ids = [row[0] for row in cursor.fetchall()]
    random.shuffle(user_ids)

    # Назначаем каждому получателя
    for i in range(len(user_ids)):
        santa_id = user_ids[i]
        recipient_id = user_ids[(i + 1) % len(user_ids)]
        cursor.execute("UPDATE users SET santa_for = ? WHERE user_id = ?", (recipient_id, santa_id))

    conn.commit()

    # Уведомляем всех участников
    for santa_id in user_ids:
        cursor.execute("SELECT gift, username FROM users WHERE user_id = (SELECT santa_for FROM users WHERE user_id = ?)", (santa_id,))
        gift, recipient_username = cursor.fetchone()
        await bot.send_message(santa_id, f"Ты стал тайным дедом для @{recipient_username}! Этот человек хочет: {gift}")


# # Обработчик для кнопки "Как бросить снежок?"
# @router.message(F.text.in_([LEXICON_RU['how_snowball']]))
# async def how_snowball(message: Message):
#     await message.answer(text=LEXICON_RU['snow'])

# # Обработчик команды "Бросить снежок"
# @router.message(lambda message: message.text.lower().startswith("бросить снежок в"))
# async def throw_snowball(message: Message):
#     # Извлекаем ID или username цели из сообщения
#     parts = message.text.split(maxsplit=3)
#     if len(parts) < 4:
#         await message.reply("Пожалуйста, укажите ID или username цели после 'бросить снежок в'.")
#         return
    
#     target = parts[3]  # ID или username цели
#     user_id = message.from_user.id

#     # Проверяем, существует ли пользователь с таким ID или username
#     cursor.execute("SELECT id, username FROM users WHERE id = ? OR username = ?", (target, target))
#     result = cursor.fetchone()
    
#     if result:
#         target_id, target_username = result
#         # Увеличиваем счетчик попаданий и обновляем список бросавших
#         cursor.execute("UPDATE users SET snowball_hits = snowball_hits + 1 WHERE id = ?", (target_id,))
#         cursor.execute("SELECT throwers FROM users WHERE id = ?", (target_id,))
#         throwers = cursor.fetchone()[0] or ""
#         throwers = f"{throwers}, {message.from_user.username}" if throwers else message.from_user.username
#         cursor.execute("UPDATE users SET throwers = ? WHERE id = ?", (throwers, target_id))
#         conn.commit()
#         await message.reply(f"Снежок брошен в @{target_username}, {message.from_user.full_name}!")
#     else:
#         await message.reply("Пользователь не найден. Укажите корректный ID или username.")

# # Обработчик для "В меня попали"
# @router.message(F.text.in_([LEXICON_RU['hit']]))
# async def show_hits(message: Message):
#     user_id = message.from_user.id
#     cursor.execute("SELECT snowball_hits, throwers FROM users WHERE user_id = ?", (user_id,))
#     hits, throwers = cursor.fetchone()
#     throwers_list = throwers.split(", ") if throwers else []
#     throwers_text = "\n".join([f"@{thrower}" for thrower in throwers_list]) if throwers_list else "никто не бросал"
#     await message.answer(
#         f"{message.from_user.full_name}, в вас попали {hits} раз(а).\n"
#         f"Бросали снежки:\n{throwers_text}"
#     )