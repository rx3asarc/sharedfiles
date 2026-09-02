"""Whisper transcription module using faster-whisper."""

import numpy as np
import re
from faster_whisper import WhisperModel
from typing import Optional
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

        # Smart formatting setup
        self.use_smart_formatting = use_smart_formatting
        self.formatter: Optional[SmartFormatter] = None

        if use_smart_formatting and openrouter_api_key and openrouter_api_key != "YOUR_API_KEY_HERE":
            try:
                self.formatter = SmartFormatter(openrouter_api_key, openrouter_model)
            except Exception as e:
                print(f"Warning: Failed to initialize smart formatter: {e}")
                self.formatter = None

        # Load model on initialization (deferred loading would hurt transcription latency)
        self.load_model()

    def load_model(self) -> None:
        """Load the Whisper model.

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
            raise TranscriberError("Model not loaded. Call load_model() first.")

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

        Uses regex patterns to add structure:
        - Bullet points for lists
        - Numbered lists for sequences
        - Proper spacing and capitalization
        - Category headers

        Runs in <1ms locally.

        Args:
            text: Raw transcription text

        Returns:
            Formatted text
        """
        if not text or not text.strip():
            return text

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Split by punctuation to find potential sentences/segments
        # Keep delimiters to reconstruct later
        segments = re.split(r'([.!?]\s+)', text)
        # Recombine: segments are like ["Sentence1", ". ", "Sentence2", ". ", ...]
        if len(segments) == 1:
            segments = [text]

        formatted_parts = []
        i = 0
        while i < len(segments):
            segment = segments[i].strip()
            if not segment:
                i += 1
                continue

            # Check if this segment is a list/introduction that should be formatted
            formatted = None

            # Pattern A: List after common verbs, with comma-separated items
            # e.g., "I need apples, bananas, and oranges" or "Buy milk, eggs, bread"
            list_verbs = r'(?:I (?:need|want|would like|am going to|plan to|should)|' \
                         r'(?:Please|Can you|Would you|Let\'s|We|You|They) (?:should|could|might|must|need to|want to|have to)|' \
                         r'(?:buy|get|pick up|grab|purchase|add|include|contains?|needs?)\s+)'
            list_match = re.match(rf'^{list_verbs}(.+?)(?:[.!?]?)$', segment, re.IGNORECASE)
            if list_match:
                items_text = list_match.group(1)
                # Smart split: commas, 'and', 'or'
                items = re.split(r',\s*(?:and\s+)?|,?\s+and\s+|,?\s+or\s+', items_text)
                items = [item.strip().rstrip('.!?') for item in items if item.strip()]

                if len(items) >= 2:
                    # Preamble before the list verb
                    preamble = segment[:list_match.start(1)].strip()
                    if preamble:
                        formatted = preamble + '\n\n' + '\n'.join(f'• {item.capitalize()}' for item in items)
                    else:
                        formatted = '\n'.join(f'• {item.capitalize()}' for item in items)

            # Pattern B: Numbered sequences using ordinals
            if not formatted and re.search(r'\b(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|1st|2nd|3rd|4th|5th|\d+\.)\b', segment, re.IGNORECASE):
                # Split by ordinal markers
                steps = re.split(
                    r'\s*(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|1st|2nd|3rd|4th|5th|\d+\.)\s*[.,:)]?\s*',
                    segment,
                    flags=re.IGNORECASE
                )
                steps = [s.strip().rstrip('.,!?') for s in steps if s.strip()]

                if len(steps) >= 2:
                    formatted = '\n'.join(f'{i+1}. {step.capitalize()}' for i, step in enumerate(steps))

            # Pattern C: Category headers with colon
            if not formatted:
                # Handle multiple categories in same segment? Split by period first
                # e.g., "Fruits: apples, bananas. Vegetables: carrots, celery."
                sub_segments = re.split(r'\.\s+', segment)
                formatted_subs = []
                for sub in sub_segments:
                    sub = sub.strip().rstrip('.!?')
                    if not sub:
                        continue
                    colon_match = re.match(r'^([^:]+):\s*(.+)$', sub)
                    if colon_match:
                        category = colon_match.group(1).strip()
                        items_text = colon_match.group(2)
                        # Split items by commas and 'and'
                        items = re.split(r',\s*|\s+and\s+', items_text)
                        items = [item.strip().rstrip('.!?') for item in items if item.strip()]
                        if len(items) >= 2:
                            formatted_subs.append(f'**{category.capitalize()}:**\n• ' + '\n• '.join(item.capitalize() for item in items))
                        else:
                            formatted_subs.append(sub.capitalize())
                    else:
                        formatted_subs.append(sub.capitalize())
                if len(formatted_subs) > 1 or any('**' in s for s in formatted_subs):
                    formatted = '\n\n'.join(formatted_subs)

            # Default: clean up
            if not formatted:
                # Capitalize first letter of the segment
                segment = segment.strip()
                if segment:
                    # Ensure first character is uppercase
                    segment = segment[0].upper() + segment[1:] if len(segment) > 1 else segment.upper()
                    # Fix spacing around punctuation
                    segment = re.sub(r'\s+([.,!?;:])', r'\1', segment)
                    segment = re.sub(r'([.,!?;:])([^\s])', r'\1 \2', segment)
                    formatted = segment

            formatted_parts.append(formatted)
            i += 1

        # Also add the separators (like ". ") if they exist
        # Actually we stripped them, but we need to join with appropriate punctuation
        # Simpler: just double newline between parts
        result = '\n\n'.join(formatted_parts)

        # Clean up
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result.strip()

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
