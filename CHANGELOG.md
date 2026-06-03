# Changelog

All notable changes to this project will be documented in this file.

The format follows a lightweight release-notes style.

## [Unreleased]

No unreleased changes yet.

## [0.1.0] - 2026-06-03

### Added

- First documented release for the Secret Santa Telegram bot.
- Stable setup instructions for local development.
- Baseline CI and project documentation.
- `.env.example` for local setup.
- GitHub Actions CI with dependency install, compile check, and module import smoke check.
- Bilingual README badges and release-ready documentation sections.
- `data/.gitkeep` so local SQLite storage has a stable runtime directory without committing database files.

### Notes

- This release focuses on packaging, documentation, and project maintainability.
- Runtime storage is local SQLite; deployments should preserve the `data/` directory.
