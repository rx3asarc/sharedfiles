# Quick Start: Switching Between Models

## Current Optimization Status
- **Model**: base (default)
- **E2E Latency**: 27.5ms (hotkey release → text in clipboard)
- **Optimizations**: 5 applied (VAD, parameters, clipboard)
- **All optimizations work with ANY model**

## Switch Models (No Progress Lost)

### Try tiny model (fastest)
```bash
python3 -m voice_tui.main --model tiny
```

### Try small model (most accurate)
```bash
python3 -m voice_tui.main --model small
```

### Benchmark all models
```bash
python3 benchmark_all_models.py
```

## Git Progress Preserved

```bash
# View all optimizations applied
git log --oneline | grep opt
# a269692 opt5: use platform-native clipboard
# 86a4d33 pivot: focus on end-to-end latency
# 34ce7c0 opt4: tune beam_size
# 36231b0 opt3: set temperature
# 06b72fa opt2: reduce best_of
# 89b4ef2 opt1: reduce VAD silence duration

# All commits survive model changes!
```

## Model Comparison

| Model | Est. Speed | Memory | Notes |
|-------|-----------|--------|-------|
| tiny | Fastest | 150MB | Good for real-time |
| base | Balanced | 380MB | Current optimized |
| small | Slower | 550MB | Best accuracy |

All use same optimizations - just switch with `--model` flag!

See [[MODEL_SWITCHING_GUIDE]] for detailed instructions.
