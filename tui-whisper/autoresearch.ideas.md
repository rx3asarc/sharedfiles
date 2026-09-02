# Autoresearch Ideas Backlog (Updated Session 2)

## Pruned Ideas (Tested, Not Viable)
- ❌ **Lazy Model Loading** - Hurts transcription latency metric
- ❌ **VAD Threshold Fine-tuning** - Tested 50-200ms range, 100ms optimal
- ❌ **Patience Parameter** - Unstable, high variance
- ❌ **condition_on_previous_text** - Slower than baseline
- ❌ **Smaller Model Sizes** - Not applicable (optimization is for base model)

## High-Impact Architecture Changes (Still Feasible)

### 1. Hardware-Accelerated VAD Integration
- [ ] Replace slower-whisper VAD with system APIs
  - Windows: Use Windows.Media.Audio voice detection
  - macOS: Use NaturalLanguage.framework voice detection
  - Linux: Use PulseAudio voice detection
  - Expected impact: 5-10% latency improvement
  - Effort: Medium (platform-specific code)
  - Status: Not attempted (requires native API research)

### 2. Streaming Transcription
- [ ] Process audio chunks as they arrive
  - Current: Wait for full recording → transcribe
  - Proposed: Transcribe chunks every 0.5-1.0s
  - Could reduce end-to-end latency by 30-50%
  - Requires: Dual-buffer architecture, partial result display
  - Effort: High (significant refactor)
  - Status: Not attempted (architecture change)

## Hardware-Accelerated Optimizations (Blocked by Hardware)
- [ ] **GPU Support (CUDA)**
  - Could provide 2-3x speedup on NVIDIA GPUs
  - Requires: CUDA-capable GPU (not available in test env)
  - Would reduce latency from 10ms to ~3-5ms
  - Priority: HIGH (biggest potential impact, but blocked)

## Architectural Improvements
- [ ] **Streaming Transcription**
  - Process audio chunks as they arrive
  - Could reduce latency by 50-70%
  - Requires refactoring audio recording pipeline
  - Priority: MEDIUM (good user experience gain)

- [ ] **Parallel Recording-Transcription**
  - Transcribe previous utterance while recording new one
  - Could hide transcription latency completely
  - Requires dual-buffer architecture

- [ ] **Lazy Model Loading**
  - Defer model initialization until first transcription
  - Could improve startup time (currently ~2s)
  - Doesn't affect transcription latency

## Inference Optimizations
- [ ] **Dynamic Batching**
  - Batch multiple audio segments
  - Not practical for real-time single-user input

- [ ] **Custom ONNX Operators**
  - Implement critical path ops in C++
  - Estimated 10-20% speedup
  - High development effort

- [ ] **Model Pruning**
  - Remove unimportant weights/layers
  - Research what % can be pruned without accuracy loss
  - Possible 15-25% speedup

- [ ] **Mixed-Precision Inference**
  - Use fp16 where accuracy permits
  - int8 already being used
  - May not help on CPU

## Packaging & Distribution
- [ ] **Pre-optimized Model Weights**
  - Quantized/pruned models distributed with app
  - Users don't need model download time
  - Requires model training/optimization

- [ ] **Compiled Python Extension**
  - Critical path in Cython/C++
  - Overkill for current performance

## Recording Optimization
- [ ] **VAD-Based Adaptive Buffer**
  - Dynamically size buffer based on speech detection
  - Could reduce audio processing overhead
  - Estimated 5% improvement

- [ ] **Hardware-Based Voice Detection**
  - Use native OS voice activity detection APIs
  - Could reduce VAD processing time from 5ms to 1ms
  - Platform-specific implementation

## Advanced Features (Beyond Optimization)
- [ ] **Live Transcript Display**
  - Show partial results as transcription proceeds
  - Would improve perceived latency
  - Requires streaming implementation

- [ ] **Language Auto-Detection**
  - Detect language from audio
  - Current: fixed to English
  - Would add ~20-30ms latency

- [ ] **Custom Vocabulary**
  - Bias model towards domain-specific terms
  - Could improve accuracy without speed change

## Status (Session 2)
- **Completed Optimizations**: 4/10 (VAD tuning, beam search reduction, greedy decoding, beam_size tuning)
- **Tested & Rejected**: Model size variations (data gathering only), patience parameter (unstable), VAD threshold fine-tuning (worse)
- **Near Limits**: Further micro-optimizations showing diminishing returns
- **High-Impact Remaining**: GPU acceleration (blocked by hardware), Streaming architecture
- **Current Performance**: 11% improvement from baseline; ~8.6ms median latency achieved
