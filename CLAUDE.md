# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python package that displays MiniMax Coding Plan token usage directly in the Claude Code CLI statusline. The statusline shows 5-hour cycle usage, weekly cycle usage, and conversation context window consumption.

## Commands

```bash
# Install in development mode
pip install -e .

# Install production
pip install .

# Run CLI directly
minimax-statusline
minimax-statusline MiniMax-M2.7

# Run check_usage module
python -m minimax_statusline.check_usage
python -m minimax_statusline.check_usage MiniMax-M2.7

# Run statusline (used by Claude Code settings.json)
python -m minimax_statusline.statusline
```

## Architecture

```
src/minimax_statusline/
├── cli.py           # Entry point for CLI command (wraps check_usage)
├── check_usage.py   # MiniMax API calls, parses token usage
└── statusline.py    # Claude Code statusline renderer (reads stdin JSON)
```

**Data flow:**
1. `statusline.py` is invoked by Claude Code with JSON context via stdin
2. It spawns `check_usage` as a subprocess to fetch MiniMax API data
3. Combines context window usage + MiniMax plan usage into two-line output

**Environment variables:**
- `MINIMAX_API_KEY` - MiniMax API key (required)
- `MINIMAX_MODEL` - Model name filter (default: MiniMax-M2.7)
- `LANG` - Language: `en` (English) or `pt-BR` (Portuguese, default)
- `MINIMAX_ENV_PATH` - Custom .env file path
- `MINIMAX_STATUSLINE_CMD` - Custom command for check_usage in statusline mode

**API endpoint:** `GET https://api.minimax.io/v1/api/openplatform/coding_plan/remains`

## Claude Code Integration

Configure in Claude Code `settings.json`:

```json
{
  "env": {
    "MINIMAX_API_KEY": "your_api_key",
    "MINIMAX_MODEL": "MiniMax-M2.7",
    "LANG": "pt-BR"
  },
  "statusLine": {
    "type": "command",
    "command": "python -m minimax_statusline.statusline"
  }
}
```
