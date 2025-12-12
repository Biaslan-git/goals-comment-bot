# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based goals comment bot. The project uses `uv` for dependency management and requires Python 3.13+.

## Development Commands

**Running the application:**
```bash
python main.py
```

**Installing dependencies (when added):**
```bash
uv sync
```

**Running with uv:**
```bash
uv run main.py
```

## Project Structure

- `main.py` - Entry point for the bot
- `pyproject.toml` - Project metadata and dependencies (managed by uv)
- `.python-version` - Python version specification

## Architecture Notes

The project is currently in initial setup phase. As the bot is developed, this file should be updated with:
- API integration details (which platform the bot comments on)
- Authentication/credential handling patterns
- Database schema if persistence is added
- Bot workflow and scheduling logic
