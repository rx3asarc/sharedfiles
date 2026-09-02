from pathlib import Path

from voice_tui.config import Config


def test_load_invalid_config_values_falls_back_to_defaults():
    scratch_dir = Path("test_output")
    scratch_dir.mkdir(exist_ok=True)
    config_file = scratch_dir / "invalid_config.yaml"

    try:
        config_file.write_text(
            "\n".join(
                [
                    "model_name: base.en this should not be here",
                    "language: 'end working, so here: v'",
                    "hotkey: ctrl+strg",
                    "sample_rate: 16000",
                ]
            ),
            encoding="utf-8",
        )

        config = Config.load(str(config_file))

        assert config.model_name == "base"
        assert config.language == "en"
        assert config.hotkey == "ctrl+shift+z"
        assert config.sample_rate == 16000
    finally:
        if config_file.exists():
            config_file.unlink()
