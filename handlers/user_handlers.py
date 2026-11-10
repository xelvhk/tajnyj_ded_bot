import logging
import os

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from keyboards.keyboards import yaded_kb
from lexicon.lexicon_ru import LEXICON_RU
from services import services

router = Router()
logger = logging.getLogger(__name__)


def admin_ids():
    return {int(value.strip()) for value in os.getenv('ADMIN_IDS', '').split(',') if value.strip().isdigit()}


def private(message: Message) -> bool:
    return message.chat.type == 'private' and message.from_user is not None


@router.message(CommandStart())
async def process_start_command(message: Message):
    if not private(message):
        return
    name = '@' + message.from_user.username if message.from_user.username else message.from_user.full_name
    result = services.register(message.from_user.id, name)
    if result == 'closed':
        await message.answer('Регистрация закрыта: жеребьёвка уже проведена.')
    else:
        await message.answer('Привет! Напиши, что хочешь получить в подарок, или «Хочу сюрприз».', reply_markup=yaded_kb)


@router.message(Command('help'))
async def help_command(message: Message):
    await message.answer('Напиши своё пожелание в личном чате с ботом. После жеребьёвки нажми «Стать тайным дедом».')


@router.message(Command('admin'))
async def admin(message: Message):
    if not private(message) or message.from_user.id not in admin_ids():
        return
    total, ready, assigned = services.status()
    await message.answer(f'Участников: {total}\nС пожеланиями: {ready}\nС назначением: {assigned}\n\n/draw — провести жеребьёвку')


@router.message(Command('draw'))
async def admin_draw(message: Message):
    if not private(message) or message.from_user.id not in admin_ids():
        return
    ids = services.draw()
    if not ids:
        await message.answer('Жеребьёвка уже проведена или готовых участников меньше двух.')
        return
    failed = 0
    for user_id in ids:
        try:
            await message.bot.send_message(user_id, 'Жеребьёвка проведена! Нажми «Стать тайным дедом», чтобы узнать получателя.')
        except Exception:
            failed += 1
            logger.exception('Failed to notify participant %s', user_id)
    await message.answer(f'Жеребьёвка проведена. Участников: {len(ids)}. Не доставлено уведомлений: {failed}.')


@router.message(F.text.in_([LEXICON_RU['yaded'], LEXICON_RU['gifts']]))
async def show_assignment(message: Message):
    if not private(message):
        return
    row = services.assignment(message.from_user.id)
    if row is None:
        await message.answer('Сначала зарегистрируйся командой /start.')
        return
    gift, name, recipient_gift = row
    text = f'Твоё пожелание: {gift or 'не указано'}'
    if name:
        text += f'\nТы даришь подарок {name}. Пожелание: {recipient_gift}'
    else:
        text += '\nЖеребьёвка ещё не проведена.'
    await message.answer(text)


@router.message(F.text & ~F.text.startswith('/'))
async def save_gift(message: Message):
    if not private(message):
        return
    gift = message.text.strip()
    if not gift:
        await message.answer('Напиши непустое пожелание.')
    elif not services.save_gift(message.from_user.id, gift):
        await message.answer('Сначала зарегистрируйся командой /start.')
    else:
        await message.answer('Пожелание сохранено!')
