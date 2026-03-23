"""
CLI entry point for minimax-statusline.

Usage:
    minimax-statusline                    # Uses default model (MiniMax-M*)
    minimax-statusline MiniMax-M*       # Specify model
    MINIMAX_MODEL=MiniMax-M* minimax-statusline

Environment variables:
    MINIMAX_API_KEY    Your MiniMax API key
    MINIMAX_MODEL     Model name (default: MiniMax-M*)
    MINIMAX_ENV_PATH  Path to .env file
"""

import os
import sys

from .check_usage import main as check_usage_main

__all__ = ["main"]


def main():
    """Entry point."""
    check_usage_main()
