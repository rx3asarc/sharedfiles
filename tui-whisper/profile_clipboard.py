#!/usr/bin/env python3
"""Profile clipboard operations - why is it so slow?"""

import time

try:
    import pyperclip
    print("Testing pyperclip clipboard operations")
    print("="*60)
    
    test_strings = [
        "short",
        "This is a medium length string for testing clipboard performance",
        "This is a much longer string. " * 20,  # ~600 chars
    ]
    
    for test_str in test_strings:
        # Test copy
        start = time.perf_counter()
        pyperclip.copy(test_str)
        copy_time = (time.perf_counter() - start) * 1000
        
        # Test paste
        start = time.perf_counter()
        retrieved = pyperclip.paste()
        paste_time = (time.perf_counter() - start) * 1000
        
        print(f"\nString length: {len(test_str)} chars")
        print(f"  Copy:  {copy_time:.2f}ms")
        print(f"  Paste: {paste_time:.2f}ms")
        print(f"  Match: {retrieved == test_str}")
        
except ImportError:
    print("pyperclip not available")

# Also test with Windows clipboard directly on Windows
try:
    import subprocess
    import sys
    
    if sys.platform == "win32":
        print("\n" + "="*60)
        print("Testing Windows clipboard directly (via clip.exe)")
        
        test_str = "Test string for Windows clipboard"
        
        start = time.perf_counter()
        # Use clip.exe (Windows command-line clipboard utility)
        process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
        process.communicate(test_str.encode('utf-8'))
        direct_time = (time.perf_counter() - start) * 1000
        
        print(f"String: {test_str}")
        print(f"  Direct (clip.exe): {direct_time:.2f}ms")
        
except Exception as e:
    print(f"Could not test Windows clipboard: {e}")
