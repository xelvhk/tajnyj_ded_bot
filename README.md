# tajnyj_ded_bot

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
python main.py
```

## Architecture
- `handlers/*`: bot command and state handlers.
- `services/*`: business logic for participants and matching.
- `database/*` or local storage: event and participant persistence.
- `config/*`: environment and runtime settings.

## Demo
- Add screenshots/GIF for:
  - event creation flow
  - participant join flow
  - private assignment delivery

## Roadmap
- [ ] Add matching constraints (avoid previous-year pairs, optional blacklist).
- [ ] Add admin commands for stats and dry-run preview.
- [ ] Add backup export/import for event state.

## Status
Active development

## License
GNU AGPLv3. See [LICENSE](LICENSE).

