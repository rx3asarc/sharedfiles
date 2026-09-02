#!/usr/bin/env python3
import sys
from voice_tui.config import Config

try:
    config = Config.load()
    print("METRIC test=100")
except Exception as e:
    print(f"ERROR: {e}")
    print("METRIC test=0")
