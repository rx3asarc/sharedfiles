"""Whisper transcription module using faster-whisper."""

import threading

import numpy as np
import re
from faster_whisper import WhisperModel
from typing import Optional, Callable
from .formatter import SmartFormatter, FormatterError


class TranscriberError(Exception):
    """Base exception for transcriber errors."""
    pass


class ModelLoadError(TranscriberError):
    """Raised when model fails to load."""
    pass


class WhisperTranscriber:
    """Transcribes audio using faster-whisper."""

    def __init__(
        self,
        model_name: str = "base",
        language: str = "en",
        device: str = "auto",
        compute_type: str = "auto",
        use_smart_formatting: bool = False,
        openrouter_api_key: str = "",
        openrouter_model: str = "qwen/qwen-2.5-7b-instruct"
    ):
        """Initialize the Whisper transcriber.

        Args:
            model_name: Model size (tiny, base, small, medium, large-v2, large-v3).
            language: Language code for transcription (e.g., 'en', 'es'), or auto.
            device: Device to use ('cpu', 'cuda', or 'auto').
            compute_type: Computation type ('int8', 'float16', 'float32', or 'auto').
            use_smart_formatting: Enable LLM-based smart formatting.
            openrouter_api_key: OpenRouter API key for smart formatting.
            openrouter_model: Model to use for formatting.

        Raises:
            ModelLoadError: If model fails to load.
        """
        self.model_name = model_name
        self.language = language
        self.device = device
        self.compute_type = compute_type
        self._model: Optional[WhisperModel] = None

        # Background-load state: the model is NOT loaded here so the TUI
        # can start instantly. start_background_load() loads it in a thread;
        # transcribe() blocks on _load_event until it is ready.
        self._load_event = threading.Event()
        self._load_lock = threading.Lock()
        self._load_started = False
        self._load_error: Optional[Exception] = None

        # Smart formatting setup
        self.use_smart_formatting = use_smart_formatting
        self.formatter: Optional[SmartFormatter] = None

        if use_smart_formatting and openrouter_api_key and openrouter_api_key != "YOUR_API_KEY_HERE":
            try:
                self.formatter = SmartFormatter(openrouter_api_key, openrouter_model)
            except Exception as e:
                print(f"Warning: Failed to initialize smart formatter: {e}")
                self.formatter = None

        # NOTE: model loading is deferred to start_background_load()/transcribe()
        # so application startup is not blocked by model load time.

    def load_model(self) -> None:
        """Load the Whisper model (blocking).

        Raises:
            ModelLoadError: If model loading fails.
        """
        try:
            # Determine device
            device = self.device
            if device == "auto":
                try:
                    import torch
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                except ImportError:
                    device = "cpu"

            # Determine compute type
            compute_type = self.compute_type
            if compute_type == "auto":
                compute_type = "float16" if device == "cuda" else "int8"

            # Load the model
            self._model = WhisperModel(
                self.model_name,
                device=device,
                compute_type=compute_type
            )

        except Exception as e:
            raise ModelLoadError(f"Failed to load model '{self.model_name}': {e}")

    def start_background_load(self, on_loaded: Optional[Callable] = None,
                              on_error: Optional[Callable] = None) -> None:
        """Load the model in a daemon thread so the TUI starts instantly.

        Args:
            on_loaded: Optional callback invoked (no args) after the model loads.
            on_error: Optional callback invoked with the exception if loading fails.
        """
        with self._load_lock:
            if self._load_started:
                return
            self._load_started = True

        def _do_load():
            try:
                self.load_model()
                self._load_event.set()
                if on_loaded:
                    try:
                        on_loaded()
                    except Exception:
                        pass
            except Exception as e:
                self._load_error = e
                self._load_event.set()
                if on_error:
                    try:
                        on_error(e)
                    except Exception:
                        pass

        threading.Thread(target=_do_load, name="whisper-model-load", daemon=True).start()

    def ensure_loaded(self) -> None:
        """Block until the model is ready, loading synchronously if needed.

        Raises:
            TranscriberError: If a background load failed.
            ModelLoadError: If a synchronous load fails.
        """
        if self._model is not None:
            return
        if self._load_started:
            self._load_event.wait()
            if self._load_error is not None:
                raise TranscriberError(f"Model failed to load: {self._load_error}")
            return
        # No background load was started (e.g. tests/direct use): load now.
        self.load_model()

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000, skip_formatting: bool = False) -> str:
        """Transcribe audio to text.

        Args:
            audio: Audio data as numpy array (float32).
            sample_rate: Sample rate of the audio (default: 16000).
            skip_formatting: If True, skip smart formatting step for faster results.

        Returns:
            Transcribed text as a string.

        Raises:
            TranscriberError: If transcription fails.
        """
        if self._model is None:
            self.ensure_loaded()

        if len(audio) == 0:
            return ""

        try:
            # Transcribe with VAD filter for better accuracy
            language = self.language
            if language is not None:
                language = str(language).strip().lower()
            if not language or language in {"auto", "detect", "none"}:
                language = None

            segments, info = self._model.transcribe(
                audio,
                language=language,
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=50),  # Faster VAD (was 100ms)
                best_of=1,
                beam_size=1,  # Optimal: speed + accuracy (beam=1 sufficient for base.en)
                temperature=0.0,
                # initial_prompt removed to reduce overhead; rely on local formatter for structure
            )

            # Combine all segments into a single string
            transcription = " ".join(segment.text.strip() for segment in segments)

            # Apply smart formatting (only if not skipped)
            if not skip_formatting:
                transcription = self._format_transcription(transcription)

            return transcription.strip()

        except Exception as e:
            raise TranscriberError(f"Transcription failed: {e}")

    def _format_transcription(self, text: str) -> str:
        """Apply fast, local formatting to transcription (no LLM).

        Produces natural, flowing text - NOT force-broken fragments:
        - Sentences run together in a single paragraph (joined with spaces),
          never pushed onto separate lines.
        - Punctuation stays attached to its sentence (no stray "." on its own line).
        - Clean capitalization and spacing.

        Structure is added ONLY when it is unambiguously intentional:
        - 2+ colon-categories with 2+ items each ("Fruits: bananas, apples.")
          become **Category:** headers with bullets.
        - Every sentence starting with an explicit number ("1. ... 2. ...")
          becomes a numbered list.
        Everything else flows as normal prose.

        Args:
            text: Raw transcription text

        Returns:
            Formatted text
        """
        if not text or not text.strip():
            return text

        # Normalize whitespace and punctuation spacing
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)                # no space before punct
        # space after sentence punctuation before LETTERS (keeps decimals like 3.5 intact)
        text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
        # space after comma/semicolon/colon before alphanumerics
        text = re.sub(r'([,;:])([A-Za-z0-9])', r'\1 \2', text)

        # Split into sentences, keeping punctuation ATTACHED (no stray delimiters).
        # Don't split after a digit-period ("1. open the app" stays together).
        sentences = [s.strip() for s in
                     re.split(r'(?<!\d\.)(?<=[.!?])\s+', text) if s.strip()]
        if not sentences:
            return text

        def _cap(s: str) -> str:
            """Capitalize the first character of a sentence."""
            if not s:
                return s
            return s[0].upper() + s[1:] if len(s) > 1 else s.upper()

        # --- 1. Category list: "Fruits: bananas, apples. Vegetables: carrots." ---
        # Allows an optional intro sentence ("I'm going shopping. ...") before
        # the category run; the trailing run of category sentences must be >= 2.
        intro_parts = []
        cat_run = []
        for sentence in sentences:
            m = re.match(r'^([A-Za-z][A-Za-z\s]{0,40}):\s*(.+)$', sentence)
            if m and ',' in m.group(2):
                items = [i.strip().rstrip('.!?') for i in
                         re.split(r',\s*|\s+and\s+', m.group(2)) if i.strip()]
                if len(items) >= 2:
                    cat_run.append((m.group(1).strip(), items))
                    continue
            if cat_run:
                break  # a non-category sentence after the run -> not a clean list
            intro_parts.append(sentence)
        if len(cat_run) >= 2:
            blocks = []
            if intro_parts:
                blocks.append(' '.join(_cap(s) for s in intro_parts))
            for cat, items in cat_run:
                blocks.append(
                    f"**{_cap(cat)}:**\n" +
                    '\n'.join(f"• {_cap(item)}" for item in items)
                )
            return '\n\n'.join(blocks)

        # --- 2. Numbered steps: "1. ... 2. ... 3. ..." ---
        steps = []
        for sentence in sentences:
            m = re.match(r'^(\d+)[\.,:)]\s+(.+)$', sentence)
            if m:
                steps.append(_cap(m.group(2)))
            else:
                steps = []
                break
        if len(steps) >= 2:
            return '\n'.join(f"{i}. {step}" for i, step in enumerate(steps, 1))

        # --- 3. Natural prose: one flowing paragraph ---
        return ' '.join(_cap(s) for s in sentences)

    @property
    def is_loaded(self) -> bool:
        """Check if model is loaded.

        Returns:
            True if model is loaded, False otherwise.
        """
        return self._model is not None

    def get_model_info(self) -> dict:
        """Get information about the loaded model.

        Returns:
            Dictionary with model information.
        """
        device = self.device
        if device == "auto":
            try:
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                device = "cpu"

        compute_type = self.compute_type
        if compute_type == "auto":
            compute_type = "float16" if device == "cuda" else "int8"

        return {
            "model_name": self.model_name,
            "language": self.language,
            "device": device,
            "compute_type": compute_type,
            "loaded": self.is_loaded
        }
