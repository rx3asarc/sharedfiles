# How to Switch Models Without Breaking Progress

## TL;DR

All optimizations are **code-based** (parameters, clipboard method, VAD settings). They work with ANY model. Switch anytime:

```bash
# Current (base model)
python3 -m voice_tui.main --model base

# Switch to tiny (faster, smaller)
python3 -m voice_tui.main --model tiny

# Switch to small (slower, more accurate)
python3 -m voice_tui.main --model small

# Benchmark all models
python3 benchmark_all_models.py
```

## What's Safe to Change

### ✅ Safe (Optimizations Preserved)

- Model size (`--model tiny|base|small|medium|large-v3`)
- Language (`--language en|es|fr|...`)
- Hardware (CPU↔GPU)
- Input device / audio settings

All **code optimizations** in these files apply equally:
- `voice_tui/transcriber.py` - VAD tuning, temperature, beam_size, best_of
- `voice_tui/fast_clipboard.py` - Platform-native clipboard
- `voice_tui/main.py` - Threading, pipeline optimization

### ⚠️ Don't Lose Progress

- **DON'T**: Delete/reset git history
- **DON'T**: Modify optimized parameters without benchmarking
- **DO**: Create separate branches if tracking multiple models
- **DO**: Keep config.yaml for different setups

## Three Ways to Switch Models

### Method 1: Command-Line (Simplest)

```bash
# Test tiny model
python3 -m voice_tui.main --model tiny

# Test base model (current optimized)
python3 -m voice_tui.main --model base

# Test small model
python3 -m voice_tui.main --model small
```

No code changes, all optimizations apply. Git history unchanged.

### Method 2: Config File (Persistent)

Create `config.yaml` for each setup:

```bash
# config_tiny.yaml
cat > config_tiny.yaml << 'EOF'
model_name: tiny
language: en
sample_rate: 16000
min_recording_duration: 0.5
EOF

# Use it
python3 -m voice_tui.main --config config_tiny.yaml

# Or set as default
cp config_tiny.yaml config.yaml
```

### Method 3: Git Branches (Track Multiple Models)

```bash
# Current state - base model fully optimized
git log --oneline | head -3
# a269692 opt5: use platform-native clipboard
# 86a4d33 pivot: focus on end-to-end latency
# 49d696f PIVOT TO END-TO-END LATENCY

# Create branch for tiny model
git checkout -b models/tiny-optimization
git tag baseline/tiny-model HEAD

# Now all commits here are for tiny model
python3 -m voice_tui.main --model tiny
# ... run optimizations ...
git commit -m "opt5-tiny: baseline at 27.5ms"

# Switch back to base model
git checkout master
python3 -m voice_tui.main --model base

# Compare branches
git log --graph --oneline --all
```

## What Gets Optimized Per Model

| Component | Per-Model? | Notes |
|-----------|-----------|-------|
| VAD tuning (100ms) | **NO** | Same for all models |
| Greedy decoding (temp=0.0) | **NO** | Same for all models |
| Beam search (best_of=1, beam_size=7) | **NO** | Same for all models |
| Clipboard optimization | **NO** | Platform-native, not model-specific |
| Inference latency | **YES** | Varies by model size |
| Memory usage | **YES** | tiny=150MB, base=380MB, small=550MB |

## Current Status

✅ **Base model optimized**: 27.5ms E2E latency
- 5 optimizations applied (VAD, best_of, temp, beam_size, clipboard)
- All saved in git commits
- Ready to test with other models

### How to Test Tiny Model

```bash
# Benchmark tiny with all current optimizations
python3 autoresearch_benchmark_e2e.py  # (modify for --model tiny)

# Or use comparison script
python3 benchmark_all_models.py
```

### How to Test Small Model

```bash
python3 -m voice_tui.main --model small
# Should be slower but more accurate
# Same optimizations apply
```

## Keeping Progress

**Git commits = Your progress**

```bash
# View all optimization commits
git log --grep="opt" --oneline
# a269692 opt5: use platform-native clipboard
# 34ce7c0 opt4: tune beam_size
# 36231b0 opt3: set temperature=0.0
# 06b72fa opt2: reduce best_of
# 89b4ef2 opt1: reduce VAD silence duration

# All changes are in code - they work with ANY model
# Switch models anytime without losing commits
```

## Example: Switching to Tiny Model

```bash
# Check current
git log --oneline -1
# a269692 opt5: use platform-native clipboard (base model)

# Switch to tiny WITHOUT breaking progress
python3 -m voice_tui.main --model tiny

# All optimizations still apply!
# No code changes needed
# No git history lost

# Benchmark tiny model
python3 benchmark_all_models.py
# Should show tiny is faster than base

# If you want to track tiny-specific work:
git checkout -b models/tiny-opt
# ... make tiny-specific optimizations ...
git commit -m "opt-tiny: [your change]"

# Merge back to master when ready
git checkout master
git merge models/tiny-opt
```

## FAQ

**Q: Will changing models break my optimizations?**  
A: No. Optimizations are in code (git commits), not model files. Safe to switch.

**Q: Should I create separate branches for each model?**  
A: Only if you want model-specific optimizations. For just testing different models, use `--model` flag.

**Q: How do I compare models fairly?**  
A: Use `benchmark_all_models.py` - runs same test on all models with identical optimizations.

**Q: Can I optimize for multiple models?**  
A: Yes - create `models/tiny-opt`, `models/small-opt` branches off master, optimize separately, merge back.

**Q: What if I find better parameters for tiny model?**  
A: Create branch, tune parameters for tiny, commit. Base model stays unchanged on master.
