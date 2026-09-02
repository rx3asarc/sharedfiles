"""Smart text formatting using LLM for better structure and readability."""

import requests
from typing import Optional
import time


class FormatterError(Exception):
    """Base exception for formatter errors."""
    pass


class SmartFormatter:
    """Format transcriptions using LLM for intelligent structuring."""

    def __init__(self, api_key: str, model: str = "qwen/qwen-2.5-7b-instruct"):
        """Initialize the smart formatter.

        Args:
            api_key: OpenRouter API key
            model: Model to use for formatting (default: qwen-2.5-7b-instruct)
        """
        self.api_key = api_key
        self.model = model
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.timeout = 10  # seconds

    def format(self, text: str) -> str:
        """Apply intelligent formatting to transcription.

        Takes raw transcription and applies:
        - Bullet points for lists
        - Numbered lists for sequences
        - Category headers
        - Proper paragraphing
        - Capitalization and punctuation

        Args:
            text: Raw transcription text

        Returns:
            Formatted text with proper structure

        Raises:
            FormatterError: If formatting fails
        """
        if not text or not text.strip():
            return text

        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            # No API key, return original
            return text

        try:
            # Prepare the prompt
            system_prompt = """You are a text formatting assistant. Your job is to take raw voice transcriptions and format them beautifully.

CRITICAL RULES - MUST FOLLOW:
1. **NEVER DELETE CONTENT** - Keep ALL words the user said, including preambles, introductions, and context
2. **PRESERVE MEANING** - The formatted output must contain EVERYTHING from the input
3. **ONLY ADD STRUCTURE** - Add bullets, numbers, headers, line breaks - but keep all original content

Formatting Guidelines:
- Detect lists and convert to bullet points (•) or numbers (1., 2., 3.)
- Add category headers in **bold** when appropriate
- Use proper capitalization and punctuation
- Keep preambles and context (e.g., "I'm going shopping" must stay!)
- If there's an introduction before a list, keep it on its own line
- Remove ONLY excessive filler words (um, uh, like, you know) - but keep natural speech
- If it's a categorized list, use headers with bullets underneath
- If it's a sequence/steps, use numbered list
- If it's just a sentence or two, clean it up but don't force list formatting

Example:
Input: "I'm going shopping. Fruits: bananas, apples. Vegetables: zucchini."
Output:
I'm going shopping.

**Fruits:**
• Bananas
• Apples

**Vegetables:**
• Zucchini

Output ONLY the formatted text, no explanations."""

            user_prompt = f"Format this transcription:\n\n{text}"

            # Make API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/your-repo/voice-tui",
                "X-Title": "Voice TUI Smart Formatter"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,  # Low temperature for consistent formatting
                "max_tokens": 1000
            }

            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                formatted_text = result['choices'][0]['message']['content'].strip()
                return formatted_text
            else:
                # API error - return original text
                error_msg = f"OpenRouter API error: {response.status_code}"
                if response.text:
                    error_msg += f" - {response.text[:200]}"
                raise FormatterError(error_msg)

        except requests.exceptions.Timeout:
            raise FormatterError("Formatting timeout - using original text")
        except requests.exceptions.ConnectionError:
            raise FormatterError("No internet connection - using original text")
        except Exception as e:
            raise FormatterError(f"Formatting failed: {e}")

    def format_safe(self, text: str) -> str:
        """Safe version that returns original text on any error.

        Args:
            text: Raw transcription text

        Returns:
            Formatted text, or original text if formatting fails
        """
        try:
            return self.format(text)
        except Exception:
            # Silently fail and return original
            return text
