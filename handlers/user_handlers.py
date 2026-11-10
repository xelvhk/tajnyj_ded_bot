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
    await message.answer(f'Участников: {total}\nС пожеланиями: {ready}\nС назначением: {assigned}\n\n/draw — предпросмотр\n/confirm_draw — жеребьёвка\n/renotify — повторная рассылка\n/new_game — новая игра')


@router.message(Command('draw'))
async def admin_draw(message: Message):
    if not private(message) or message.from_user.id not in admin_ids():
        return
    total, ready, assigned = services.status()
    if assigned:
        await message.answer('Жеребьёвка уже проведена.')
        return
    if ready < 2:
        await message.answer('Для жеребьёвки нужны хотя бы два участника с пожеланиями.')
        return
    people = services.roster()
    lines = [f'{name[:80]} — {"готов" if has_gift else "нет пожелания"}' for name, has_gift in people]
    preview = '\n'.join(lines)
    if len(preview) > 3500:
        preview = preview[:3500] + '\n…'
    await message.answer(f'Готовы: {ready} из {total}. Без пожелания: {total - ready}.\n{preview}\nДля окончательного запуска введи /confirm_draw.')


@router.message(Command('confirm_draw'))
async def confirm_draw(message: Message):
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


@router.message(Command('renotify'))
async def renotify(message: Message):
    if not private(message) or message.from_user.id not in admin_ids():
        return
    ids = services.assigned_ids()
    if not ids:
        await message.answer('Назначений пока нет.')
        return
    failed = 0
    for user_id in ids:
        try:
            await message.bot.send_message(user_id, 'Твоё назначение доступно по кнопке «Стать тайным дедом».')
        except Exception:
            failed += 1
            logger.exception('Failed to notify participant %s', user_id)
    await message.answer(f'Повторно отправлено: {len(ids) - failed}. Ошибок: {failed}.')


@router.message(Command('new_game'))
async def preview_new_game(message: Message):
    if not private(message) or message.from_user.id not in admin_ids():
        return
    total, ready, assigned = services.status()
    await message.answer(f'Текущая игра: {total} участников, {assigned} назначений. /confirm_new_game сохранит архив базы и очистит список для новой игры.')


@router.message(Command('confirm_new_game'))
async def confirm_new_game(message: Message):
    if not private(message) or message.from_user.id not in admin_ids():
        return
    path = services.new_game()
    if path is None:
        await message.answer('Список уже пуст.')
    else:
        await message.answer(f'Новая игра создана. Архив: {path.name}')


@router.message(F.text.in_([LEXICON_RU['yaded'], LEXICON_RU['gifts']]))
async def show_assignment(message: Message):
    if not private(message):
        return
    row = services.assignment(message.from_user.id)
    if row is None:
        await message.answer('Сначала зарегистрируйся командой /start.')
        return
    gift, name, recipient_gift = row
    if services.status()[2] and not name:
        await message.answer('Жеребьёвка завершена. Ты не участвовал, потому что пожелание не было указано вовремя.')
        return
    text = f"Твоё пожелание: {gift or 'не указано'}"
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
    elif services.status()[2]:
        await message.answer('Жеребьёвка завершена. Пожелания больше не меняются.')
    elif not services.save_gift(message.from_user.id, gift):
        await message.answer('Сначала зарегистрируйся командой /start.')
    else:
        await message.answer('Пожелание сохранено!')
