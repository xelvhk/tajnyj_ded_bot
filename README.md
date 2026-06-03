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

## Known Limitations
- The bot currently uses local SQLite storage, so deployment should preserve the `data/` directory.
- Matching starts after a fixed participant threshold in the current implementation.
- There is no admin dry-run preview yet.

## Roadmap
- [ ] Add matching constraints (avoid previous-year pairs, optional blacklist).
- [ ] Add admin commands for stats and dry-run preview.
- [ ] Add backup export/import for event state.
- [ ] Add smoke tests for matching logic.

## Status
Active development

## Changelog
See [CHANGELOG.md](CHANGELOG.md).

## License
GNU AGPLv3. See [LICENSE](LICENSE).
