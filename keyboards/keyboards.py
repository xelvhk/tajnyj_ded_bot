from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from lexicon.lexicon_ru import LEXICON_RU


# Создаем кнопки клавиатуры
yaded_button_1 = KeyboardButton(text=LEXICON_RU['yaded'])
yaded_button_2 = KeyboardButton(text=LEXICON_RU['snow'])

yaded_kb = ReplyKeyboardMarkup(
    keyboard=[[yaded_button_1],
              [yaded_button_2]
              ],
    resize_keyboard=True
)