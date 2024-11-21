from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from lexicon.lexicon_ru import LEXICON_RU


# Создаем кнопки клавиатуры
yaded_button_1 = KeyboardButton(text=LEXICON_RU['yaded'])
yaded_button_2 = KeyboardButton(text=LEXICON_RU['gifts'])
# yaded_button_3 = KeyboardButton(text=LEXICON_RU['how_snowball'])
# yaded_button_4 = KeyboardButton(text=LEXICON_RU['hit'])

yaded_kb = ReplyKeyboardMarkup(
    keyboard=[[yaded_button_1],
              [yaded_button_2]
              # [yaded_button_3],
              # [yaded_button_4]
              ],
    resize_keyboard=True
)