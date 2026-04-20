# AGENTS.md — Edge AI Add-on for nRF Connect SDK

## Project Overview

This is Nordic Semiconductor's **Edge AI Add-on** for the nRF Connect SDK (NCS). It is a Zephyr RTOS module that provides on-device ML inference on Nordic nRF54x SoCs, using two backends:

- **Axon NPU** — Nordic's dedicated neural processing unit peripheral, accessed through a pre-compiled driver library and compiler toolchain
- **Neuton** — CPU-based inference (Cortex-M4/M33), provided as a pre-compiled static library

The module integrates into an NCS workspace via west (`west.yml`) and depends on `sdk-nrf v3.3.0-preview2` with full Zephyr beneath it.

**License**: `LicenseRef-Nordic-5-Clause` (all source file headers carry SPDX identifiers).

## Build System

This is a **Zephyr module** — it does not build standalone. It must be used within an NCS/west workspace.

### Prerequisites

- nRF Connect SDK (NCS) toolchain (west, Zephyr SDK)
- Python 3.12
- Doxygen 1.12.0 (for doc builds)

### Building samples/applications

Follow standard NCS build flow from an NCS workspace:

```bash
west build -b nrf54lm20dk/nrf54lm20b/cpuapp -d build applications/ww_kws
west build -b nrf54lm20dk/nrf54lm20b/cpuapp -d build samples/axon/hello_axon
```

Some applications use sysbuild (`sysbuild: true` in `sample.yaml`).

### Building documentation

```bash
cd doc
make html
```

Requires `pip install -r doc/requirements.txt -r doc/requirements_ci.txt` and west to have resolved dependencies.

### Building tests

Tests are Zephyr twister-compatible. The inference test builds for `nrf54lm20dk/nrf54lm20b/cpuapp`:

```bash
west twister -T tests -b
```

The test model name is selected via Kconfig (`CONFIG_NRF_AXON_MODEL_NAME`) or overridden with environment variable `NRF_AXON_MODEL_NAME`.

### Simulator builds

The Axon driver and platform code support non-Zephyr simulator builds (Linux, macOS, Windows). The CMakeLists.txt files branch on `NOT_A_ZEPHYR_BUILD` to handle simulator vs. target paths. Simulator builds link pre-compiled libraries from `lib/axon/bin/`.

## Architecture

### Directory Layout

```
├── include/           # Public API headers
│   ├── nrf_edgeai/    # Edge AI runtime, DSP, NN abstraction
│   │   ├── rt/        # Runtime: init, feed, infer, decode pipeline
│   │   ├── dsp/       # DSP primitives (FFT, statistics, spectral, windowing)
│   │   ├── nn/        # Neural network abstraction (Neuton + Axon backends)
│   │   └── platform/  # Compiler-agnostic platform macros
│   └── drivers/axon/  # Axon NPU driver public API
├── lib/
│   ├── nrf_edgeai/    # Pre-compiled Edge AI runtime (.a for Cortex-M4/M33)
│   └── axon/          # Axon platform abstraction layer
│       └── platform/  # Platform source (Zephyr + simulator implementations)
├── drivers/axon/      # Axon NN inference driver (open-source wrapper code)
├── applications/      # Full demo applications
├── samples/           # Smaller sample applications
├── tests/             # Test applications (Zephyr twister)
├── tools/axon/compiler/ # Axon TFLite compiler (Python, runs in Docker)
├── doc/               # Sphinx documentation
├── zephyr/            # Zephyr module glue (module.yml, top-level CMakeLists.txt, Kconfig)
└── scripts/           # Utility scripts
```

### Data Flow: nRF Edge AI Runtime (High-Level API)

The `nrf_edgeai` runtime provides a 3-step pipeline for model inference:

1. **`nrf_edgeai_init()`** — Initialize runtime context
2. **`nrf_edgeai_feed_inputs()`** — Feed raw sensor data sample-by-sample; returns `NRF_EDGEAI_ERR_INPROGRESS` until the input window is full
3. **`nrf_edgeai_run_inference()`** — Run inference on the filled window; results in `p_edgeai->decoded_output`

The runtime internally dispatches to either Neuton or Axon backend based on model type (`NRF_EDGEAI_MODEL_NEUTON` vs `NRF_EDGEAI_MODEL_AXON`).

### Data Flow: Axon Direct API (Low-Level)

For direct Axon NPU access without the Edge AI runtime:

1. **`nrf_axon_nn_model_validate()`** — Check model + buffer sizes
2. **`nrf_axon_nn_model_init_vars()`** — Initialize persistent variables for streaming models
3. **`nrf_axon_nn_model_infer_sync()`** — Synchronous inference (blocking), OR
4. **`nrf_axon_nn_model_async_init()` + `nrf_axon_nn_model_infer_async()`** — Async inference with callback
5. **`nrf_axon_nn_get_classification()`** — Post-process classification output

### Key Shared Buffers

- **Interlayer buffer** — Shared scratch memory for NN layer intermediates. Size configured via `CONFIG_NRF_AXON_INTERLAYER_BUFFER_SIZE`. All models share this buffer; only one inference can run at a time.
- **PSUM buffer** — Partial sum buffer for specific NN operations. Configured via `CONFIG_NRF_AXON_PSUM_BUFFER_SIZE`. Default is 0 (not needed for most models).
- **Persistent vars** — Per-model state that survives between inferences (for streaming models with VarHandle ops). Initialized via `nrf_axon_nn_model_init_vars()`.

### Model Task Types

- Classification (multiclass / binary)
- Regression
- Anomaly detection

### Input Data Types

Models accept `I8`, `I16`, or `F32` input (`nrf_edgeai_input_type_t`). Axon models use quantized input with parameters (`quant_mult`, `quant_round`, `quant_zp`) defined in the compiled model header.

## Code Style and Conventions

### C Code

- **Tabs** for indentation (width 8), enforced by `.editorconfig` and `.clang-format`
- **Max line length**: 100 characters
- **Brace style**: Linux (opening brace on same line for functions, next line for control structures — see `.clang-format` `BreakBeforeBraces: Linux`)
- **Naming**: `nrf_<subsystem>_<entity>_<variant>` pattern
  - Types: `nrf_edgeai_<name>_t` (typedef'd structs/enums)
  - Functions: `nrf_edgeai_<verb>_<object>()` or `nrf_axon_nn_<verb>()`
  - Structs: `nrf_edgeai_<name>_s` / `nrf_axon_<name>_s` (typedef'd to `_t`)
  - Enums: `nrf_edgeai_<name>_e` (typedef'd to `_t`)
  - Constants/Macros: `NRF_EDGEAI_` or `NRF_AXON_` prefix, UPPER_SNAKE_CASE
  - Private/internal headers: placed in `private/` subdirectories
- **`#pragma once`** used in some Axon headers; `#ifndef _GUARD_H_` pattern used in nrf_edgeai headers
- **`extern "C"`** guards in all public headers
- **Doxygen** groups: `@defgroup` / `@ingroup` for API documentation
- **Return codes**: Axon uses `nrf_axon_result_e` (0 = success, negative = error, positive = status); Edge AI runtime uses `nrf_edgeai_err_t` (0 = success, 126 = in-progress, negative = error)

### Python

- 4-space indentation
- Used in compiler toolchain (`tools/axon/compiler/scripts/`)

### Kconfig

- Tab indentation (width 8)
- Config symbols prefixed with `NRF_AXON_` or `NRF_EDGEAI_`

### CMake

- 2-space indentation
- `cmake_minimum_required(VERSION 3.13.0)` or `3.20.0` for tests
- Zephyr module CMake uses `zephyr_sources()`, `zephyr_include_directories()`, `zephyr_compile_definitions()`, `zephyr_link_libraries()`
- Non-Zephyr builds check `${NOT_A_ZEPHYR_BUILD}`

## Compliance and CI

### Compliance Checks (PR)

Run via `compliance.yml` on PRs. Uses Zephyr's `check_compliance.py` with these checks enabled:

- ClangFormat, KconfigBasicNoModules, SysbuildKconfigBasicNoModules, LicenseAndCopyrightCheck, BinaryFiles, GitLint, PyLint, Ruff

The compliance check **excludes** generated code:

```
--exclude .*/nrf_edgeai_generated
--exclude .*/generated
--exclude tests/axon/compiled_models
```

### checkpatch

Configured in `.checkpatch.conf` with max line length 100 and many Zephyr-specific suppressions. Same exclusions for generated code.

### Required file header

All source files must have the copyright + SPDX license header:

```c
/*
 * Copyright (c) 20XX Nordic Semiconductor ASA
 *
 * SPDX-License-Identifier: LicenseRef-Nordic-5-Clause
 */
```

## Generated Code

Multiple directories contain **auto-generated code** that must not be hand-edited or linted:

- `**/nrf_edgeai_generated/` — Generated by Nordic Edge AI Lab (model code for applications/samples)
- `**/generated/` — Generated Axon model headers (e.g., `samples/axon/hello_axon/src/generated/`)
- `tests/axon/compiled_models/` — Compiled model headers with test vectors

These are excluded from checkpatch and compliance checks. They follow naming patterns like `nrf_edgeai_user_model.c`, `nrf_edgeai_user_model.h`, `nrf_edgeai_user_types.h`, `nrf_edgeai_user_model_axon.h`.

## Axon Compiler

Located at `tools/axon/compiler/`. It compiles TFLite models into Axon NPU command buffers.

- **Runs in Docker/Podman** — see `run_docker.sh` / `run_docker.bat`
- **Input**: YAML config file referencing a TFLite model
- **Output**: C header file (`nrf_axon_model_<name>_.h`) containing the compiled model struct
- **Python dependencies**: TensorFlow 2.19.0, numpy, scikit-learn, matplotlib, pyyaml, cffi

### Key Gotcha: Axon vs TFLite Data Formats

The Axon NPU uses different internal data layout from TFLite. Input/output tensors may be unpacked (padded rows) in the interlayer buffer. Use `nrf_axon_nn_copy_output_to_packed_buffer()` to get packed output, or work with the interlayer buffer directly when you control synchronization.

## Important Kconfig Options

| Option | Description |
|--------|-------------|
| `CONFIG_NRF_AXON` | Enable Axon NPU support |
| `CONFIG_NRF_AXON_INTERLAYER_BUFFER_SIZE` | Interlayer buffer size in bytes — **must be ≥ largest model's requirement** |
| `CONFIG_NRF_AXON_PSUM_BUFFER_SIZE` | PSUM buffer size (0 = disabled, needed for some models) |
| `CONFIG_NRF_AXON_INTERLAYER_BUFFER_MEMREGION_NAME` | Memory section for interlayer buffer (default `.bss`) |
| `CONFIG_NRF_AXON_MODEL_NAME` | Model name for test builds |

## Gotchas and Non-Obvious Patterns

1. **Interlayer buffer is shared** — Only one model can use Axon at a time. The driver manages mutual exclusion via `nrf_axon_platform_reserve_for_user()` / `nrf_axon_platform_free_reservation_from_user()`. Synchronous inference APIs handle this internally; for async or direct buffer access you must be aware of ownership.

2. **Output stride ≠ packed width** — Axon interlayer buffer rows may be wider than the actual data (alignment padding). Always use `nrf_axon_nn_copy_output_to_packed_buffer()` to extract packed results, or account for stride when reading directly.

3. **Quantization parameters are per-model** — Each compiled model header defines `quant_mult`, `quant_round`, `quant_zp` for inputs and `dequant_mult`, `dequant_round`, `dequant_zp` for outputs. These must be used for float↔int8 conversion; they differ per model.

4. **`nrf_edgeai_feed_inputs()` returns INPROGRESS** — The Edge AI runtime collects samples into a window. You must keep calling it until it returns `NRF_EDGEAI_ERR_SUCCESS`, indicating the window is full and you can call `nrf_edgeai_run_inference()`.

5. **Persistent vars need explicit initialization** — Streaming models with VarHandle ops require `nrf_axon_nn_model_init_vars()` at session start. It's harmless to call on non-streaming models.

6. **Pre-compiled libraries** — The core Axon driver and Edge AI runtime are pre-compiled static libraries (`lib/axon/bin/`, `lib/nrf_edgeai/cortex-m*/`). The open-source code in `drivers/axon/` and `lib/axon/platform/` is the wrapper/platform layer. When `NRF_AXON_DEV_BUILD` is defined, internal development paths activate.

7. **FPU variant** — On Zephyr targets with FPU enabled (`CONFIG_FPU`), a different Axon driver library is linked (`nrf-axon-driver-internal-fpu`).

8. **Sample YAML test definitions** — Tests and samples define their test harness in `sample.yaml` files using Zephyr twister syntax. The `harness: console` with regex patterns is used for validation (e.g., checking "PASS COUNT" output).

9. **Board overlays** — Many samples require board-specific `.overlay` files (devicetree overlays) for the Axon NPU peripheral. These are in `boards/` directories under each sample.

10. **Module path** — When used as a Zephyr module via west, this repo is placed at `edge-ai/` in the NCS workspace (see `west.yml` `self: path: edge-ai`). Headers are included relative to `include/` (e.g., `#include <nrf_edgeai/nrf_edgeai.h>`).
