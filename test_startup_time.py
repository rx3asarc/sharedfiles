#!/usr/bin/env python3
"""Test startup time with lazy model loading."""

import sys
import time
from pathlib import Path

# Time just the import and init
start_total = time.perf_counter()

sys.path.insert(0, str(Path(__file__).parent))

start_import = time.perf_counter()
from voice_tui.transcriber import WhisperTranscriber
import_time = (time.perf_counter() - start_import) * 1000

start_init = time.perf_counter()
transcriber = WhisperTranscriber(model_name="base")
init_time = (time.perf_counter() - start_init) * 1000

total_time = (time.perf_counter() - start_total) * 1000

print("Startup Time with Lazy Loading")
print("="*50)
print(f"Import: {import_time:.0f}ms")
print(f"Init: {init_time:.0f}ms")
print(f"Total: {total_time:.0f}ms")
print()
print("Expected: Init should be nearly instant (<100ms)")
print("          First transcription will include model loading")
