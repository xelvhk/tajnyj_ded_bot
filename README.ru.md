# tajnyj_ded_bot

[![CI](https://github.com/xelvhk/tajnyj_ded_bot/actions/workflows/ci.yml/badge.svg)](https://github.com/xelvhk/tajnyj_ded_bot/actions/workflows/ci.yml)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/xelvhk/tajnyj_ded_bot)](https://github.com/xelvhk/tajnyj_ded_bot/commits/main)

Telegram-бот для «Тайного Санты»: управление участниками, случайное распределение и приватная выдача пар.

Язык: [English](README.md) | **Русский**

## Проблема
- «Тайного Санту» часто организуют вручную в чатах или таблицах.
- Ручное распределение приводит к ошибкам и вопросам справедливости.
- Участникам нужен простой и приватный способ получить назначение.

## Стек
- Python 3.11+
- Aiogram (Telegram Bot API)
- SQLite/локальное хранилище

## Setup
```bash
git clone https://github.com/xelvhk/tajnyj_ded_bot.git
cd tajnyj_ded_bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
 # Укажите BOT_TOKEN и ADMIN_IDS в .env
python main.py
```

## Администрирование

Укажите числовые Telegram ID администраторов через запятую в `ADMIN_IDS` файла `.env`. В личном чате `/admin` показывает число зарегистрированных, готовых и распределённых участников. Команда `/draw` проводит жеребьёвку среди участников, указавших пожелание (минимум двое). Она необратима через бот и повторно пары не меняет. После жеребьёвки новая регистрация закрыта. Уведомления могут не доставиться; назначение сохраняется и доступно участнику по кнопке. Для новой игры требуется отдельно подготовить новую базу; перед любыми действиями с базой сохраните резервную копию.

Проверка логики: `python -m unittest discover -s tests -v`.

## Архитектура
- `handlers/*`: обработчики команд и состояний.
- `services/*`: бизнес-логика участников и распределения.
- `data/santas.db`: локальная SQLite-база, создается во время работы.
- `config_data/*`: переменные окружения и runtime-настройки.
- `keyboards/*`: reply-клавиатуры.
- `lexicon/*`: русские сообщения бота.

## Demo
- Добавить скриншоты/GIF:
  - создание события
  - вступление участников
  - приватная выдача пары

## Ограничения
- Сейчас бот использует локальную SQLite-базу, поэтому при деплое нужно сохранять директорию `data/`.
- Распределение запускает администратор; в него входят только участники с пожеланием.
- Пока нет admin dry-run preview перед финальной жеребьевкой.

## Roadmap
- [ ] Добавить ограничения распределения (исключение прошлогодних пар, optional blacklist).
- [ ] Добавить предпросмотр участников перед жеребьёвкой.
- [ ] Добавить экспорт/импорт бэкапа состояния события.
- [x] Добавить базовые тесты логики распределения.

## Статус
Active development

## Changelog
См. [CHANGELOG.md](CHANGELOG.md).

## Лицензия
GNU AGPLv3. См. [LICENSE](LICENSE).
