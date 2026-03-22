"""
CLI entry point for minimax-statusline.

Usage:
    minimax-statusline                    # Uses default model (MiniMax-M2.7)
    minimax-statusline MiniMax-M2.5       # Specify model
    MINIMAX_MODEL=MiniMax-M2.7 minimax-statusline

Environment variables:
    MINIMAX_API_KEY    Your MiniMax API key
    MINIMAX_MODEL     Model name (default: MiniMax-M2.7)
    MINIMAX_ENV_PATH  Path to .env file
"""

import os
import sys

from .check_usage import main as check_usage_main

__all__ = ["main"]


def main():
    """Entry point."""
    check_usage_main()
