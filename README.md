# tajnyj_ded_bot

[![CI](https://github.com/xelvhk/tajnyj_ded_bot/actions/workflows/ci.yml/badge.svg)](https://github.com/xelvhk/tajnyj_ded_bot/actions/workflows/ci.yml)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/xelvhk/tajnyj_ded_bot)](https://github.com/xelvhk/tajnyj_ded_bot/commits/main)

Telegram Secret Santa bot for managing participants, random matching, and private gift exchange flow.

Language: **English** | [Русский](README.ru.md)

## Problem
- Secret Santa events are often organized manually in chats or spreadsheets.
- Manual pairing creates mistakes and fairness issues.
- Participants need a simple and private way to receive assignments.

## Stack
- Python 3.11+
- Aiogram (Telegram Bot API)
- SQLite/local persistence

## Setup
```bash
git clone https://github.com/xelvhk/tajnyj_ded_bot.git
cd tajnyj_ded_bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set BOT_TOKEN and comma-separated numeric ADMIN_IDS in .env
python main.py
```

## Architecture
- `handlers/*`: bot command and state handlers.
- `services/*`: business logic for participants and matching.
- `data/santas.db`: local SQLite database created at runtime.
- `config_data/*`: environment and runtime settings.
- `keyboards/*`: reply keyboard definitions.
- `lexicon/*`: Russian bot messages.

## Demo
- Add screenshots/GIF for:
  - event creation flow
  - participant join flow
  - private assignment delivery

## Administration
Set numeric Telegram admin IDs in `ADMIN_IDS`. Admin commands work in private chat:
- `/admin` shows statistics and commands.
- `/draw` previews participants and returns `/confirm_draw <code>` to assign recipients to users with wishes (at least two).
- `/renotify` retries only undelivered reminders.
- `/new_game` returns `/confirm_new_game <code>` to archive the current database in `data/archive/` and start a new game. Preserve the whole `data/` directory on deployment.

Once matching is complete, registration and wish edits are closed. Participants without a wish are excluded. Confirmation codes expire after ten minutes or when the roster or wishes change.

Run service tests: `python -m unittest discover -s tests -v`.

## Roadmap
- [ ] Add matching constraints (avoid previous-year pairs, optional blacklist).
- [ ] Add archive export/import.
- [x] Add admin commands and matching preview.
- [x] Add basic matching tests.

## Status
Active development

## Changelog
See [CHANGELOG.md](CHANGELOG.md).

## License
GNU AGPLv3. See [LICENSE](LICENSE).
