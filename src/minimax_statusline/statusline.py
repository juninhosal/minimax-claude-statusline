"""
Statusline renderer for Claude Code.

Reads Claude Code's JSON status input from stdin and produces a
two-line statusline output.

Usage (via Claude Code settings.json):
    "statusLine": {
        "type": "command",
        "command": "python path/to/statusline.py"
    }

Environment variables:
    MINIMAX_MODEL            Model name to show (default: MiniMax-M2.7)
    MINIMAX_STATUSLINE_CMD   Full command to run check_usage (optional)
                             Defaults to installed package call.
"""

import json
import os
import subprocess
import sys
import shutil

# Load .env file for LANG and other env vars
try:
    from dotenv import load_dotenv
    # Try default locations
    default_env = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, ".env")
    for path in [default_env, ".env", ".env.example"]:
        if os.path.exists(path):
            load_dotenv(path)
            break
except ImportError:
    pass

MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-M2.7")


def get_i18n():
    """Get translations based on LANG env var."""
    lang = os.getenv("LANG", "en")
    if lang.startswith("pt"):
        return {
            "used": "usado",
            "context": "Contexto",
        }
    return {
        "used": "used",
        "context": "Context",
    }


def get_term_width() -> int:
    """Return terminal width or 80 as fallback."""
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80


def build_bar(pct: float, width: int = 10) -> str:
    """Build ASCII progress bar."""
    filled = int(pct * width / 100)
    empty = width - filled
    return "|" + "#" * filled + "-" * empty + "|"


def parse_stdin() -> dict:
    """Parse JSON input from Claude Code."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        return json.loads(raw)
    except Exception:
        return {}


def get_minimax_line() -> str:
    """Run check_usage and return its output."""
    cmd = os.getenv("MINIMAX_STATUSLINE_CMD")

    if not cmd:
        # Use installed package
        cmd = f'{sys.executable} -m minimax_statusline.check_usage {MODEL}'

    try:
        env = os.environ.copy()
        # Ensure LANG is passed to subprocess
        if "LANG" not in env:
            env["LANG"] = os.getenv("LANG", "en")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            shell=True,
            timeout=30,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def main():
    data = parse_stdin()
    term_w = get_term_width()
    minimax_line = get_minimax_line()

    # ── Startup case: no context data yet ──────────────────────────────────
    if not data:
        sys.stdout.write(minimax_line.ljust(term_w - 1))
        return

    # ── Normal case: has context from Claude Code ───────────────────────────
    ctx = data.get("context_window", {})
    used_pct = float(ctx.get("used_percentage") or 0)
    bar = build_bar(used_pct, width=10)
    model_name = data.get("model", {}).get("display_name", MODEL)
    i18n = get_i18n()

    line1 = f"{model_name}  {i18n['context']} {bar} {used_pct:.0f}% {i18n['used']}"
    line2 = minimax_line.split("\n")[0] if minimax_line else ""

    sys.stdout.write(line1.ljust(term_w - 1) + "\n")
    sys.stdout.write(line2.ljust(term_w - 1))


if __name__ == "__main__":
    main()
