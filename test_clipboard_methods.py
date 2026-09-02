#!/usr/bin/env python3
"""Test different clipboard methods to find the fastest."""

import time
import subprocess
import sys

test_text = "This is a test string for clipboard benchmarking. " * 10  # ~500 chars

print("Testing Clipboard Methods")
print("="*60)

# Test 1: clip.exe directly
print("\n1. Windows clip.exe (current fast_clipboard):")
for i in range(3):
    start = time.perf_counter()
    process = subprocess.Popen(
        ['clip'],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    process.communicate(test_text.encode('utf-8', errors='replace'), timeout=1.0)
    elapsed = (time.perf_counter() - start) * 1000
    print(f"  Run {i+1}: {elapsed:.2f}ms")

# Test 2: pyperclip
print("\n2. pyperclip (old method):")
try:
    import pyperclip
    for i in range(3):
        start = time.perf_counter()
        pyperclip.copy(test_text)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"  Run {i+1}: {elapsed:.2f}ms")
except ImportError:
    print("  Not available")

# Test 3: Direct Windows API via ctypes
print("\n3. Windows API via ctypes (fastest possible):")
if sys.platform == "win32":
    import ctypes
    import ctypes.wintypes
    
    try:
        for i in range(3):
            start = time.perf_counter()
            
            # Copy to clipboard using Windows API
            text_bytes = test_text.encode('utf-8')
            text_c = ctypes.c_char_p(text_bytes)
            
            # Allocate global memory
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GlobalAlloc(0x0002, len(text_bytes) + 1)  # GMEM_MOVEABLE
            ptr = kernel32.GlobalLock(handle)
            ctypes.memmove(ptr, text_c, len(text_bytes) + 1)
            kernel32.GlobalUnlock(handle)
            
            # Open clipboard
            user32 = ctypes.windll.user32
            user32.OpenClipboard(None)
            user32.EmptyClipboard()
            user32.SetClipboardData(1, handle)  # CF_TEXT
            user32.CloseClipboard()
            
            elapsed = (time.perf_counter() - start) * 1000
            print(f"  Run {i+1}: {elapsed:.2f}ms")
    except Exception as e:
        print(f"  Error: {e}")
else:
    print("  Windows only")

print()
print("Note: Subprocess overhead is ~18-20ms on Windows")
print("      This may be inherent to how Windows launches processes")
print("      Windows API direct access might be faster")
