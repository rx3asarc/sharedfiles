"""Fast clipboard operations using platform-native methods."""

import sys
import subprocess

# Windows API direct access (ultra-fast)
_WINDOWS_API_AVAILABLE = False
if sys.platform == "win32":
    try:
        import ctypes
        import ctypes.wintypes
        _WINDOWS_API_AVAILABLE = True
    except ImportError:
        pass


def _copy_to_clipboard_windows_api(text: str) -> bool:
    """Copy to Windows clipboard using Windows API (0.1ms - ultra fast).
    
    Uses CF_UNICODETEXT for full Unicode support.
    
    Args:
        text: Text to copy
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import ctypes
        
        # Convert text to UTF-16LE (Windows Unicode) with null terminator
        # Windows expects a null-terminated UTF-16LE string
        text_utf16 = text.encode('utf-16-le', errors='replace')
        # Add null terminator (2 zero bytes)
        data = text_utf16 + b'\x00\x00'
        size = len(data)
        
        # Windows API functions
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        
        # Allocate global movable memory
        handle = kernel32.GlobalAlloc(0x0002, size)  # GMEM_MOVEABLE
        if not handle:
            with open("debug.log", "a") as f:
                f.write("[CLIPBOARD] Windows API: GlobalAlloc failed\n")
            return False
        
        # Lock memory and copy data
        ptr = kernel32.GlobalLock(handle)
        if not ptr:
            kernel32.GlobalFree(handle)
            with open("debug.log", "a") as f:
                f.write("[CLIPBOARD] Windows API: GlobalLock failed\n")
            return False
        
        try:
            # Copy bytes to allocated memory
            ctypes.memmove(ptr, data, size)
            kernel32.GlobalUnlock(handle)
            
            # Open clipboard and set data
            if not user32.OpenClipboard(None):
                kernel32.GlobalFree(handle)
                with open("debug.log", "a") as f:
                    f.write("[CLIPBOARD] Windows API: OpenClipboard failed\n")
                return False
            
            try:
                user32.EmptyClipboard()
                # CF_UNICODETEXT = 13
                user32.SetClipboardData(13, handle)
                # Success: Windows takes ownership of the handle, do not free
                return True
            finally:
                user32.CloseClipboard()
        except Exception as e:
            kernel32.GlobalFree(handle)
            raise
            
    except Exception as e:
        with open("debug.log", "a") as f:
            f.write(f"[CLIPBOARD] Windows API exception: {type(e).__name__}: {e}\n")
        # If Windows API fails, fall back to subprocess
        return False


def copy_to_clipboard(text: str) -> bool:
    """Copy text to clipboard using fastest available method.
    
    Windows: Uses Windows API directly (0.1ms) - fastest
    Fallback: Uses clip.exe (16ms), then pyperclip
    macOS: Uses pbcopy
    Linux: Uses xclip or xsel, then pyperclip
    
    Args:
        text: Text to copy
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open("debug.log", "a") as f:
            f.write(f"[CLIPBOARD] Attempting copy, platform={sys.platform}, windows_api_available={_WINDOWS_API_AVAILABLE}\n")
        if sys.platform == "win32" and _WINDOWS_API_AVAILABLE:
            # Windows: Use Windows API directly - ULTRA FAST (0.1ms!)
            ok = _copy_to_clipboard_windows_api(text)
            with open("debug.log", "a") as f:
                f.write(f"[CLIPBOARD] Windows API result: {ok}\n")
            if ok:
                return True
            # If Windows API failed, fall back to clip.exe
            with open("debug.log", "a") as f:
                f.write("[CLIPBOARD] Windows API failed, falling back to clip.exe\n")
            try:
                process = subprocess.Popen(
                    ['clip'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                process.communicate(text.encode('utf-8', errors='replace'), timeout=1.0)
                ok = process.returncode == 0
                with open("debug.log", "a") as f:
                    f.write(f"[CLIPBOARD] clip.exe result: {ok}, returncode={process.returncode}\n")
                if ok:
                    return True
            except FileNotFoundError:
                with open("debug.log", "a") as f:
                    f.write("[CLIPBOARD] clip.exe not found\n")
            except Exception as e:
                with open("debug.log", "a") as f:
                    f.write(f"[CLIPBOARD] clip.exe exception: {e}\n")
            # Final fallback to pyperclip
            with open("debug.log", "a") as f:
                f.write("[CLIPBOARD] Trying pyperclip fallback\n")
            try:
                import pyperclip
                pyperclip.copy(text)
                with open("debug.log", "a") as f:
                    f.write("[CLIPBOARD] pyperclip success\n")
                return True
            except Exception as e:
                with open("debug.log", "a") as f:
                    f.write(f"[CLIPBOARD] pyperclip exception: {e}\n")
                return False
        
        elif sys.platform == "win32":
            # No Windows API available, use clip.exe directly
            with open("debug.log", "a") as f:
                f.write("[CLIPBOARD] Using clip.exe (no Windows API)\n")
            try:
                process = subprocess.Popen(
                    ['clip'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                process.communicate(text.encode('utf-8', errors='replace'), timeout=1.0)
                ok = process.returncode == 0
                with open("debug.log", "a") as f:
                    f.write(f"[CLIPBOARD] clip.exe result: {ok}, returncode={process.returncode}\n")
                if ok:
                    return True
            except FileNotFoundError:
                with open("debug.log", "a") as f:
                    f.write("[CLIPBOARD] clip.exe not found\n")
            except Exception as e:
                with open("debug.log", "a") as f:
                    f.write(f"[CLIPBOARD] clip.exe exception: {e}\n")
            # Fallback to pyperclip
            with open("debug.log", "a") as f:
                f.write("[CLIPBOARD] Trying pyperclip fallback\n")
            try:
                import pyperclip
                pyperclip.copy(text)
                with open("debug.log", "a") as f:
                    f.write("[CLIPBOARD] pyperclip success\n")
                return True
            except Exception as e:
                with open("debug.log", "a") as f:
                    f.write(f"[CLIPBOARD] pyperclip exception: {e}\n")
                return False
            
        elif sys.platform == "darwin":
            # macOS: use pbcopy
            with open("debug.log", "a") as f:
                f.write("[CLIPBOARD] Using pbcopy\n")
            try:
                process = subprocess.Popen(
                    ['pbcopy'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                process.communicate(text.encode('utf-8', errors='replace'), timeout=1.0)
                ok = process.returncode == 0
                with open("debug.log", "a") as f:
                    f.write(f"[CLIPBOARD] pbcopy result: {ok}, returncode={process.returncode}\n")
                if ok:
                    return True
            except FileNotFoundError:
                with open("debug.log", "a") as f:
                    f.write("[CLIPBOARD] pbcopy not found\n")
            except Exception as e:
                with open("debug.log", "a") as f:
                    f.write(f"[CLIPBOARD] pbcopy exception: {e}\n")
            # Fallback to pyperclip
            with open("debug.log", "a") as f:
                f.write("[CLIPBOARD] Trying pyperclip fallback\n")
            try:
                import pyperclip
                pyperclip.copy(text)
                with open("debug.log", "a") as f:
                    f.write("[CLIPBOARD] pyperclip success\n")
                return True
            except Exception as e:
                with open("debug.log", "a") as f:
                    f.write(f"[CLIPBOARD] pyperclip exception: {e}\n")
                return False
            
        elif sys.platform == "linux":
            # Linux: try xclip first, then xsel, then pyperclip
            with open("debug.log", "a") as f:
                f.write("[CLIPBOARD] Using linux xclip/xsel\n")
            for cmd in [['xclip', '-selection', 'clipboard'], ['xsel', '--clipboard', '--input']]:
                try:
                    process = subprocess.Popen(
                        cmd,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    process.communicate(text.encode('utf-8', errors='replace'), timeout=1.0)
                    if process.returncode == 0:
                        with open("debug.log", "a") as f:
                            f.write(f"[CLIPBOARD] {cmd[0]} succeeded\n")
                        return True
                except FileNotFoundError:
                    with open("debug.log", "a") as f:
                        f.write(f"[CLIPBOARD] {cmd[0]} not found\n")
                    continue
                except Exception as e:
                    with open("debug.log", "a") as f:
                        f.write(f"[CLIPBOARD] {cmd[0]} exception: {e}\n")
                    continue
            # Fallback to pyperclip
            with open("debug.log", "a") as f:
                f.write("[CLIPBOARD] Trying pyperclip fallback\n")
            try:
                import pyperclip
                pyperclip.copy(text)
                with open("debug.log", "a") as f:
                    f.write("[CLIPBOARD] pyperclip success\n")
                return True
            except Exception as e:
                with open("debug.log", "a") as f:
                    f.write(f"[CLIPBOARD] pyperclip exception: {e}\n")
                return False
        else:
            # Unknown platform: try pyperclip
            with open("debug.log", "a") as f:
                f.write("[CLIPBOARD] Unknown platform, trying pyperclip\n")
            try:
                import pyperclip
                pyperclip.copy(text)
                with open("debug.log", "a") as f:
                    f.write("[CLIPBOARD] pyperclip success\n")
                return True
            except Exception as e:
                with open("debug.log", "a") as f:
                    f.write(f"[CLIPBOARD] pyperclip exception: {e}\n")
                return False
                
    except Exception as e:
        # Unexpected top-level exception
        with open("debug.log", "a") as f:
            f.write(f"[CLIPBOARD] Unexpected exception: {type(e).__name__}: {e}\n")
        return False
