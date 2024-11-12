from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from keyboards.keyboards import yaded_kb
from lexicon.lexicon_ru import LEXICON_RU

router = Router()
bot = Bot

# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'],
                         reply_markup=yaded_kb)


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])

# Обработчик нажатий на кнопки
@router.message(F.text.in_([LEXICON_RU['yaded']]))
async def ded(message: Message):
    await message.reply("Сейчас определим, кому дарить подарки")
