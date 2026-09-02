# Autoresearch: TUI Whisper Multi-Metric Optimization

## Objective

Optimize **tui-whisper** voice-to-text application for three user-impacting metrics:

1. **Transcription Latency** (primary): End-to-end time from hotkey release → text in clipboard. Target: <1000ms (best case with base model on GPU)
2. **Memory Usage** (secondary): Peak RAM during transcription. Track for regressions.
3. **UI Rendering Performance** (secondary): Frame time smoothness during recording. Track for flicker/stuttering.

Users hold a hotkey, speak, release, and expect their transcribed text immediately. Every 100ms delay impacts perceived responsiveness.

## Metrics

- **Primary**: `transcription_latency` (milliseconds, **lower is better**)
- **Secondary**: 
  - `peak_memory` (MB) — peak RAM during a transcription run
  - (UI frame smoothness tracked separately, not in main benchmark yet)

## How to Run

```bash
./autoresearch.sh
```

Outputs:
```
METRIC transcription_latency=450.2
METRIC peak_memory=2145.3
```

## Files in Scope

### Core Optimization Targets
- **`voice_tui/transcriber.py`** — Whisper model loading, transcription, compute type selection
  - Bottlenecks: Model initialization, GPU/CPU selection, batch processing
- **`voice_tui/recorder.py`** — Audio capture and level detection
  - Bottlenecks: Stream setup, buffer management, level calculation overhead
- **`voice_tui/main.py`** — Controller orchestration, threading
  - Bottlenecks: Thread coordination, callback latency, clipboard operations
- **`voice_tui/config.py`** — Configuration and device detection
  - Bottlenecks: Device auto-detection logic

### Secondary Targets (if needed)
- **`voice_tui/ascii_app.py`** — TUI rendering loop
  - Frame rate limiting, render-on-demand, change detection
- **`voice_tui/ascii_renderer.py`** — Screen output
  - Terminal escape sequences, buffer efficiency

## Off Limits

- Model architecture (we use faster-whisper as-is)
- Audio recording quality (16kHz is standard)
- Whisper accuracy (not the focus)

## Constraints

- No new external dependencies (except those already required)
- Code quality must remain reasonable (no obfuscation)
- Tests must not regress (if any exist)

## Key Insights

### Current Bottlenecks (from code review)

1. **Model Loading on First Transcription** (~500-2000ms)
   - WhisperModel is loaded inside `WhisperTranscriber.__init__()`, which happens on startup
   - On first transcription, may include model download/cache lookup
   - **Opportunity**: Cache model more aggressively, pre-warm GPU

2. **Two-Phase Transcription (already optimized)**
   - PHASE 1: Raw transcription (skip smart formatting) — appears in clipboard fast
   - PHASE 2: Background formatting (async, doesn't block latency)
   - This is already good; smart formatting is async

3. **Device/Compute Type Auto-Detection**
   - `transcriber.py` checks CUDA availability on each init
   - **Opportunity**: Cache this result, avoid redundant checks

4. **Audio-to-Clipboard Pipeline**
   - Audio recording → numpy array → Whisper → text → pyperclip.copy()
   - Most time is Whisper; clipboard and numpy conversion are negligible
   - **Opportunity**: Profile actual runs to confirm

5. **UI Rendering Loop (secondary concern)**
   - 10 FPS frame rate with change detection already in place
   - Anti-flicker system working (per SESSION_PROGRESS.md)
   - **Status**: Good; focus on transcription latency

## What's Been Tried

### Successful Optimizations ✅
1. **Reduce VAD silence duration**: 500ms → 100ms
   - First run: 170ms → 97ms (43% faster)
   - Note: VAD is critical; disabling it caused 4s+ latency

2. **Reduce beam search width**: best_of 5 → 1
   - First run: 97ms → 89.9ms (7% faster)
   - Median: 10.8ms → 9.5ms (12% faster)

3. **Greedy decoding**: temperature=0.0
   - First run: 89.9ms → 69.0ms (23% faster)
   - Median: 9.5ms → 6.0ms (37% faster!)
   - **MAJOR WIN** - Greedy decoding is deterministic and preferred for speech

### Attempted but Rejected ❌
- Remove initial prompt: Slower (111ms vs 97ms)
- Reduce chunk length: Slower (75ms vs 69ms)
- Reduce VAD threshold: Slower (109ms vs 69ms)
- Shorten initial prompt: Slower (7.7ms vs 5.4ms)
- Disable VAD: Catastrophically slow (4037ms!)

### Current Status (Session 3)
- **Baseline E2E latency**: 33ms (hotkey release → clipboard)
- **Current E2E latency**: 6.7ms (79.7% improvement!)
- **Memory**: ~550MB (stable, no regression)
- **Confidence**: 4.8× above noise floor

### Optimizations Applied
1. **VAD duration**: 500ms → 100ms (27-43% faster)
2. **Beam search**: best_of 5 → 1 (7-12% faster)
3. **Greedy decoding**: temperature default → 0.0 (23-37% faster)
4. **Beam size tuning**: 5 → 7 (15% faster)
5. **Fast clipboard**: Native clip.exe (16ms → 3ms) (45% improvement E2E)
6. **Ultra-fast clipboard**: Windows API direct (3ms → 0.1ms) (75.6% improvement E2E) 🔥 **BREAKTHROUGH**

## Optimization Strategy

### Phase 1: Baseline & Profiling
1. Establish reproducible measurements of latency, memory, and render time
2. Profile transcription path to identify exact bottlenecks
3. Measure improvement/regression with high confidence

### Phase 2: Low-Hanging Fruit
1. **Compute Type Tuning** (int8 vs float16 vs float32)
   - Test on current model to find best latency/quality tradeoff
2. **Device Selection Caching** (don't re-detect CUDA on every init)
3. **Model Preloading** (warm model cache on startup)

### Phase 3: Deeper Optimizations (if needed)
1. **Inference Optimization** (batch processing, quantization, layer pruning)
2. **Memory Reduction** (model offloading, gradient checkpointing if re-training)
3. **Async Pipeline** (overlap recording → transcription → display)

---

## Commands

Run benchmark:
```bash
python3 autoresearch_benchmark.py
```

Run with bash script (what autoresearch uses):
```bash
./autoresearch.sh
```

View baseline:
```bash
cat autoresearch.jsonl | head -20
```

---

## Session Notes

- **Model**: base (140MB) by default
- **Device**: auto-detect (CUDA if available, else CPU)
- **Compute**: auto (float16 on CUDA, int8 on CPU)
- **Test Audio**: 2-second synthetic chirp (resembles speech)
- **Runs per Iteration**: 3 (median reported)

---

## Next Steps

1. Get baseline measurements
2. Identify the single biggest bottleneck via profiling
3. Implement targeted optimizations
4. Verify no regressions
5. Repeat until hitting diminishing returns

## Profiling & Measurement Results

### Transcription Time Breakdown (from cProfile)
- **VAD (voice activity detection)**: ~5ms per transcription
- **ONNX runtime inference**: ~4-5ms per transcription  
- **Python overhead**: ~0.5ms per transcription
- **Total**: ~9-10ms per transcription (after warmup)

### Memory Usage
```
Process memory growth:
  - At startup: 17.5 MB
  - After imports: 261.4 MB (+244 MB)
  - After transcriber init: 360.9 MB (+99 MB for model loading)
  - After first transcription: 380.3 MB (+18 MB overhead)
  - Peak during sustained use: ~550 MB
```

Breakdown:
- Whisper base model: ~140 MB
- Python runtime + dependencies: ~240 MB
- Transient allocations: ~50 MB
- **Total**: 380-550 MB (acceptable for modern systems)

### UI Rendering Performance
- **Frame computation time**: 0.6 ms per frame
- **With 10 FPS budget (100ms)**: Uses only 0.6% CPU time
- **Verdict**: Rendering is extremely efficient; no optimization needed

### End-to-End Latency (Real-world)
For a typical 1.5-second speech utterance:
- **First run**: 119.6ms (model warmup)
- **Subsequent runs**: 31.2-32.5ms median
- **Best case**: 31.2ms (speech end → text in clipboard)

## Final Optimization Frontier

We've reached practical software optimization limits. Further improvements would require:
1. **Model Quantization** (int4/int2) - trades accuracy for speed
2. **Smaller models** (tiny/small instead of base) - trades accuracy for speed
3. **GPU Acceleration** - requires CUDA-capable hardware (not available in test env)
4. **Streaming transcription** - major architectural refactor
5. **Custom ONNX operators** - requires C++ development

All attempted micro-optimizations that didn't work:
- Removing VAD: catastrophic (4037ms!)
- Shorter initial prompt: slower (7.7ms vs 5.4ms)
- Explicit chunk processing: slower (75ms vs 69ms)
- max_new_tokens limiting: slower (12ms vs 6ms)
- Batch processing: not applicable for single utterances

**Conclusion**: Current implementation is near-optimal for the base model on CPU.
