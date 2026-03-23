"""
Check MiniMax Coding Plan token usage via API.

API Endpoint:
    GET https://api.minimax.io/v1/api/openplatform/coding_plan/remains

Usage:
    python -m minimax_statusline.check_usage [model_name]

    # Example:
    python -m minimax_statusline.check_usage MiniMax-M*

Environment variables:
    MINIMAX_API_KEY       Your MiniMax API key (required)
    MINIMAX_MODEL         Model name to filter (default: MiniMax-M*)
    MINIMAX_ENV_PATH      Path to .env file (optional)
"""

import os
import sys

try:
    import requests
except ImportError:
    print("Erro: 'requests' nao instalado. Execute: pip install minimax-statusline")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("Erro: 'python-dotenv' nao instalado. Execute: pip install minimax-statusline")
    sys.exit(1)


# ── Default .env path (project root) ─────────────────────────────────────────
DEFAULT_ENV_PATH = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, ".env")


def load_api_key(env_path: str | None = None) -> str:
    """Load MINIMAX_API_KEY from environment or .env file."""
    if env_path:
        load_dotenv(env_path)
    else:
        # Try default locations
        for path in [DEFAULT_ENV_PATH, ".env", ".env.example"]:
            if os.path.exists(path):
                load_dotenv(path)
                break

    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        print("Erro: MINIMAX_API_KEY nao encontrada.")
        print("Crie um arquivo .env com: MINIMAX_API_KEY=sua_chave_aqui")
        print("Ou export MINIMAX_API_KEY=sua_chave_aqui")
        sys.exit(1)
    return api_key


def get_model_data(api_key: str, model_name: str) -> dict | None:
    """Fetch usage data from MiniMax API for a specific model."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    url = "https://api.minimax.io/v1/api/openplatform/coding_plan/remains"

    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexao: {e}")
        sys.exit(1)

    base = data.get("base_resp", {})
    if base.get("status_code") != 0:
        print(f"Erro da API: {base.get('status_msg')} (code={base.get('status_code')})")
        sys.exit(1)

    models = data.get("model_remains", [])
    if not models:
        print("Nenhum dado de modelo encontrado.")
        sys.exit(1)

    target = next((m for m in models if m.get("model_name") == model_name), None)
    if not target:
        available = [m.get("model_name") for m in models]
        print(f"Modelo '{model_name}' nao encontrado.")
        print(f"Modelos disponiveis: {', '.join(available)}")
        sys.exit(1)

    return target


def format_ms(ms: int) -> str:
    """Format milliseconds to Xh Ym."""
    s = ms / 1000
    h, rem = divmod(int(s), 3600)
    m, _ = divmod(rem, 60)
    return f"{h}h{m}m"


def get_i18n():
    """Get translations based on LANG env var."""
    lang = os.getenv("LANG", "en")
    if lang.startswith("pt"):
        return {
            "used": "restante",
            "week": "semana",
            "reset": "reset",
        }
    return {
        "used": "used",
        "week": "week",
        "reset": "reset",
    }


def format_usage(target: dict, model_name: str) -> str:
    """Format usage data as a single-line string."""
    i18n = get_i18n()

    interval_total = target.get("current_interval_total_count", 0)
    interval_used = target.get("current_interval_usage_count", 0)
    interval_remaining = interval_total - interval_used
    interval_pct = 100 - (interval_remaining / interval_total * 100) if interval_total else 0
    interval_reset_ms = target.get("remains_time", 0)

    weekly_total = target.get("current_weekly_total_count", 0)
    weekly_used = target.get("current_weekly_usage_count", 0)
    weekly_remaining = weekly_total - weekly_used
    weekly_pct = 100 - (weekly_remaining / weekly_total * 100) if weekly_total else 0
    weekly_reset_ms = target.get("weekly_remains_time", 0)

    return (
        f"[{model_name}] "
        f"5H:{interval_pct:.0f}% {i18n['used']} "
        f"{i18n['reset']}:{format_ms(interval_reset_ms)} | "
        f"{i18n['week']}:{weekly_pct:.0f}% {i18n['used']} "
        f"{i18n['reset']}:{format_ms(weekly_reset_ms)}"
    )


def main():
    # Load .env first so MINIMAX_MODEL is available
    api_key = load_api_key()
    model_name = os.getenv("MINIMAX_MODEL") or (
        sys.argv[1] if len(sys.argv) > 1 else "MiniMax-M*"
    )
    target = get_model_data(api_key, model_name)
    print(format_usage(target, model_name))


if __name__ == "__main__":
    main()
