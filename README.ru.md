# tajnyj_ded_bot

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
python main.py
```

## Архитектура
- `handlers/*`: обработчики команд и состояний.
- `services/*`: бизнес-логика участников и распределения.
- `database/*` или локальное хранилище: состояние событий и участников.
- `config/*`: переменные окружения и runtime-настройки.

## Demo
- Добавить скриншоты/GIF:
  - создание события
  - вступление участников
  - приватная выдача пары

## Roadmap
- [ ] Добавить ограничения распределения (исключение прошлогодних пар, optional blacklist).
- [ ] Добавить admin-команды со статистикой и dry-run preview.
- [ ] Добавить экспорт/импорт бэкапа состояния события.

## Статус
Active development

## Лицензия
GNU AGPLv3. См. [LICENSE](LICENSE).

