---
name: video-intelligence
description: Watch and analyze a local video with Gemini. Produces grounded general, creative, or repurposing reports with timestamps, verbatim on-screen text and dialogue where discernible, plus clear confidence boundaries. Use for ads, TikToks, UGC, tutorials, demos, webinars, Looms, meetings, and screen recordings.
argument-hint: <path/to/video.mp4> [--mode general|creative|repurpose] [--prompt "..."] [--fps N] [--model ...]
disable-model-invocation: true
allowed-tools: Bash, Read
---

# Video Intelligence

Analyze a local video using Gemini's native video understanding.

## Prerequisites

- Python 3.10+
- `google-genai` installed: `python3 -m pip install google-genai`
- `GEMINI_API_KEY` exported in the current shell

## Steps

1. Parse `$ARGUMENTS`. The first argument is a required video path. Supported optional flags are `--mode`, `--prompt`, `--fps`, `--model`, `--timeout`, and `--keep-upload`.
2. Verify the path exists before invoking the script.
3. Run the script from this installed skill directory:

```bash
python3 scripts/analyze_video.py $ARGUMENTS
```

4. Present the Markdown printed to stdout without rewriting its confidence labels. Progress logs are deliberately emitted on stderr.

## Modes

- `general`: evidence-based video record: summary, timeline, audio, visual details, and notable moments.
- `creative`: general report plus hook, audience, angle, tension, payoff, CTA, and transferable patterns. Strategy claims must be labelled as inference.
- `repurpose`: content inventory plus formats, clips, and angle directions grounded in the source.

## Accuracy requirements

- Never invent speaker names, creators, brands, dialogue, visible text, or a voiceover.
- Preserve uncertainty. State "unclear" or "not discernible" when appropriate.
- Quote visible text and dialogue only when it can be read or heard confidently.
- In creative mode, distinguish a direct observation from an interpretation or recommendation.

## Troubleshooting

- If the key is absent, ask the user to export `GEMINI_API_KEY` and open a new terminal.
- If the default model is unavailable in their account, ask them to pass a model ID available to their Gemini account.
- If fast cuts or small text matter, rerun with `--fps 2` or `--fps 4`.
- If processing times out, rerun with a higher `--timeout` value or a shorter clip.
