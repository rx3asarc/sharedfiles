"""Configuration management for voice-tui."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None


@dataclass
class Config:
    """Application configuration with defaults."""

    model_name: str = "base"
    language: str = "en"
    hotkey: str = "ctrl+shift+z"
    sample_rate: int = 16000
    min_recording_duration: float = 0.5
    device_type: str = "auto"  # auto, cpu, cuda
    compute_type: str = "auto"  # auto, int8, float16, float32
    auto_type: bool = False  # (legacy) Enable auto-typing at cursor position
    auto_paste: bool = True  # Automatically paste clipboard after transcription
    type_interval: float = 0.01  # Seconds between keystrokes (for auto_type)
    use_smart_formatting: bool = False  # Enable LLM-based smart formatting
    openrouter_api_key: str = ""  # OpenRouter API key for smart formatting
    openrouter_model: str = "qwen/qwen-2.5-7b-instruct"  # Model to use for formatting
    config_path: Optional[str] = None  # Track where config was loaded from

    VALID_MODELS = {
        "tiny.en",
        "tiny",
        "base.en",
        "base",
        "small.en",
        "small",
        "medium.en",
        "medium",
        "large-v1",
        "large-v2",
        "large-v3",
        "large",
        "distil-large-v2",
        "distil-medium.en",
        "distil-small.en",
        "distil-large-v3",
        "distil-large-v3.5",
        "large-v3-turbo",
        "turbo",
    }
    VALID_HOTKEY_MODIFIERS = {"ctrl", "alt", "shift", "win"}
    VALID_HOTKEY_KEYS = {
        "space",
        "tab",
        "enter",
        "esc",
        "escape",
        "backspace",
        "delete",
        "insert",
        "home",
        "end",
        "pageup",
        "pagedown",
        "up",
        "down",
        "left",
        "right",
    }

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """Load configuration from YAML file if exists, otherwise use defaults.

        Args:
            config_path: Path to config.yaml file. If None, looks in current directory.

        Returns:
            Config instance with loaded or default values.
        """
        try:
            import yaml
        except ImportError:
            yaml = None
        config_data = {}

        if config_path is None:
            config_path = "config.yaml"

        config_file = Path(config_path)

        if config_file.exists() and yaml is not None:
            try:
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Failed to load config file: {e}")
                print("Using default configuration.")

        instance = cls(
            model_name=cls._validate_model_name(config_data.get('model_name', cls.model_name)),
            language=cls._validate_language(config_data.get('language', cls.language)),
            hotkey=cls._validate_hotkey(config_data.get('hotkey', cls.hotkey)),
            sample_rate=config_data.get('sample_rate', cls.sample_rate),
            min_recording_duration=config_data.get('min_recording_duration', cls.min_recording_duration),
            device_type=config_data.get('device_type', cls.device_type),
            compute_type=config_data.get('compute_type', cls.compute_type),
            auto_type=config_data.get('auto_type', cls.auto_type),
            auto_paste=config_data.get('auto_paste', cls.auto_paste),
            type_interval=config_data.get('type_interval', cls.type_interval),
            use_smart_formatting=config_data.get('use_smart_formatting', cls.use_smart_formatting),
            openrouter_api_key=config_data.get('openrouter_api_key', cls.openrouter_api_key),
            openrouter_model=config_data.get('openrouter_model', cls.openrouter_model),
        )
        instance.config_path = str(config_file)
        return instance

    @classmethod
    def _validate_model_name(cls, value) -> str:
        if isinstance(value, str):
            candidate = value.strip().lower()
            if candidate in cls.VALID_MODELS:
                return candidate
        return cls.model_name

    @classmethod
    def _validate_language(cls, value) -> str:
        if isinstance(value, str):
            candidate = value.strip().lower()
            if candidate == "auto" or re.fullmatch(r"[a-z]{2,5}", candidate):
                return candidate
        return cls.language

    @classmethod
    def _validate_hotkey(cls, value) -> str:
        if not isinstance(value, str):
            return cls.hotkey

        parts = [part.strip().lower() for part in value.split("+") if part.strip()]
        if len(parts) < 2:
            return cls.hotkey

        modifiers = parts[:-1]
        key = parts[-1]

        if len(set(modifiers)) != len(modifiers):
            return cls.hotkey
        if any(modifier not in cls.VALID_HOTKEY_MODIFIERS for modifier in modifiers):
            return cls.hotkey
        if cls._is_valid_hotkey_key(key):
            return "+".join(modifiers + [key])

        return cls.hotkey

    @classmethod
    def _is_valid_hotkey_key(cls, key: str) -> bool:
        if key in cls.VALID_HOTKEY_KEYS:
            return True
        if len(key) == 1 and key.isalnum():
            return True
        if re.fullmatch(r"f([1-9]|1[0-2])", key):
            return True
        return False

    def update_from_args(self, args) -> None:
        """Update configuration from command-line arguments.

        Args:
            args: Parsed argparse.Namespace object.
        """
        if hasattr(args, 'model') and args.model:
            self.model_name = args.model
        if hasattr(args, 'language') and args.language:
            self.language = args.language
        if hasattr(args, 'hotkey') and args.hotkey:
            self.hotkey = args.hotkey

    def save(self, config_path: Optional[str] = None) -> None:
        """Save configuration to YAML file.

        Args:
            config_path: Path to save config file. If None, uses the path it was loaded from.

        Raises:
            RuntimeError: If yaml library is not available
            IOError: If file cannot be written
        """
        try:
            import yaml
        except ImportError:
            yaml = None
        if yaml is None:
            raise RuntimeError("PyYAML is not installed. Cannot save configuration.")

        save_path = config_path or self.config_path or "config.yaml"

        config_data = {
            'model_name': self.model_name,
            'language': self.language,
            'hotkey': self.hotkey,
            'sample_rate': self.sample_rate,
            'min_recording_duration': self.min_recording_duration,
            'device_type': self.device_type,
            'compute_type': self.compute_type,
            'auto_type': self.auto_type,
            'auto_paste': self.auto_paste,
            'type_interval': self.type_interval,
            'use_smart_formatting': self.use_smart_formatting,
            'openrouter_api_key': self.openrouter_api_key,
            'openrouter_model': self.openrouter_model,
        }

        with open(save_path, 'w') as f:
            yaml.safe_dump(config_data, f, default_flow_style=False, sort_keys=False)
