# Activity Model — Input Data Format

<!--
Copyright (c) 2026 Nordic Semiconductor ASA
SPDX-License-Identifier: LicenseRef-Nordic-5-Clause
-->

## Overview

The activity detection model takes **150 int8 values** representing a
**50-sample window of triaxial accelerometer data** and classifies it
into one of 7 activities.

| Property         | Value                                          |
|------------------|------------------------------------------------|
| Input shape      | `[1, 1, 150, 1]` (batch × H × W × channels)   |
| Input type       | `int8_t` (quantized)                           |
| Input size       | 150 bytes                                      |
| Output shape     | `[1, 1, 7, 1]` — one score per class           |
| Output type      | `int8_t` (quantized logits, no softmax)         |
| Classes          | sitting, standing, lying_down, walking, running, cycling, workout |
| Inference time   | ~14138 Axon ticks                              |

## Sensor Requirements

| Property      | Value           |
|---------------|-----------------|
| Axes          | X, Y, Z accel   |
| Sample rate   | 100 Hz          |
| Window size   | 50 samples      |
| Window duration | 0.5 seconds   |

## Input Layout

Samples are collected from the accelerometer at 100 Hz and arranged in
an interleaved fashion — one triplet (X, Y, Z) per time step:

```
Index:   0    1    2    3    4    5    6    7    8   ...  147  148  149
Axis:    X0   Y0   Z0   X1   Y1   Z1   X2   Y2   Z2  ...  X49  Y49  Z49
```

In C:

```c
#define WINDOW_SIZE  50
#define NUM_AXES     3
#define NUM_FEATURES (WINDOW_SIZE * NUM_AXES)

float window[NUM_FEATURES];

for (int s = 0; s < WINDOW_SIZE; s++) {
    float xyz[3];
    read_accel_sample(xyz);   /* your sensor read function */

    window[s * NUM_AXES + 0] = xyz[0];  /* X */
    window[s * NUM_AXES + 1] = xyz[1];  /* Y */
    window[s * NUM_AXES + 2] = xyz[2];  /* Z */
}
```

## Normalization (Critical)

The training data was normalized using **per-axis z-score normalization**
(mean subtraction + std division, computed per axis across all training data).
The per-axis means and stds are saved in `output/activity_model_meta.txt`.

**The same normalization must be applied on the device before quantization.**
Skipping this step will cause the model to see a completely different data
distribution and accuracy will drop dramatically.

```
axis_means: 0.123456,0.234567,0.345678
axis_stds:  5.678901,6.789012,7.890123
```

```c
#define AXIS_MEANS  { 0.123456f, 0.234567f, 0.345678f }
#define AXIS_STDS   { 5.678901f, 6.789012f, 7.890123f }

/* After collecting window[] with raw m/s² values (interleaved XYZ): */
for (int s = 0; s < WINDOW_SIZE; s++) {
    for (int a = 0; a < NUM_AXES; a++) {
        window[s * NUM_AXES + a] = (window[s * NUM_AXES + a] - axis_means[a])
                                   / axis_stds[a];
    }
}
```

## Quantization

After normalization, the float values (now in the range approximately `[-1, +1]`)
must be quantized to `int8_t`. The quantization parameters are embedded in the
compiled model header (`outputs/nrf_axon_model_activity_model_.h`) and are
also listed in the metadata file:

| Parameter  | Value             | Source              |
|------------|-------------------|---------------------|
| quant_mult | 103280891         | Model header        |
| quant_round| 19                | Model header        |
| quant_zp   | -27               | Model header        |

Quantization formula:

```c
static void quantize_window(const float *src, int8_t *dst, size_t len,
                            const nrf_axon_nn_compiled_model_input_s *input)
{
    const uint32_t q_mult  = input->quant_mult;
    const uint8_t  q_round = input->quant_round;
    const int8_t   q_zp    = input->quant_zp;

    for (size_t i = 0; i < len; i++) {
        dst[i] = (int8_t)((uint32_t)(src[i] * q_mult) >> q_round) + q_zp;
    }
}
```

## Complete Pipeline (Axon Direct API)

```c
#include "nrf_axon_model_activity_model_.h"

#define WINDOW_SIZE         50
#define NUM_AXES            3
#define NUM_FEATURES        (WINDOW_SIZE * NUM_AXES)
#define AXIS_MEANS          { 0.123456f, 0.234567f, 0.345678f }  /* from meta file */
#define AXIS_STDS           { 5.678901f, 6.789012f, 7.890123f }  /* from meta file */

static float  window_float[NUM_FEATURES];
static int8_t input_q8[NUM_FEATURES];
static int8_t output_q8[64];

void activity_inference_loop(void)
{
    const nrf_axon_nn_compiled_model_input_s *model_input =
        &model_ACTIVITY_MODEL.inputs[model_ACTIVITY_MODEL.external_input_ndx];

    while (1) {
        /* 1. Collect 50 samples (0.5 s @ 100 Hz) */
        collect_window(window_float);

        /* 2. Per-axis z-score normalize */
        const float means[3] = AXIS_MEANS;
        const float stds[3]  = AXIS_STDS;
        for (int s = 0; s < WINDOW_SIZE; s++) {
            for (int a = 0; a < NUM_AXES; a++) {
                window_float[s * NUM_AXES + a] =
                    (window_float[s * NUM_AXES + a] - means[a]) / stds[a];
            }
        }

        /* 3. Quantize float -> int8 */
        quantize_window(window_float, input_q8, NUM_FEATURES, model_input);

        /* 4. Run inference on Axon NPU */
        nrf_axon_nn_model_infer_sync(&model_ACTIVITY_MODEL,
                                     input_q8, output_q8);

        /* 5. Get classification result */
        int32_t score;
        int16_t class_idx = nrf_axon_nn_get_classification(
            &model_ACTIVITY_MODEL, output_q8, NULL, &score);

        /* class_idx: 0=sitting, 1=standing, 2=lying_down,
                      3=walking,  4=running,  5=cycling,
                      6=workout                          */
    }
}
```

## Output Interpretation

The model outputs 7 `int8_t` raw logits (no softmax). The predicted class
is the index of the maximum value:

```c
int argmax = 0;
int8_t max_val = output_q8[0];
for (int i = 1; i < 7; i++) {
    if (output_q8[i] > max_val) {
        max_val = output_q8[i];
        argmax = i;
    }
}
```

Or use the Axon helper:

```c
int32_t score;
int16_t class_idx = nrf_axon_nn_get_classification(
    &model_ACTIVITY_MODEL, output_q8, NULL, &score);
```

### Class Index Mapping

| Index | Activity   |
|-------|------------|
| 0     | sitting    |
| 1     | standing   |
| 2     | lying_down |
| 3     | walking    |
| 4     | running    |
| 5     | cycling    |
| 6     | workout    |

### Dequantization (optional)

If you need floating-point confidence scores, dequantize the output logits:

| Parameter        | Value       |
|------------------|-------------|
| dequant_mult     | from model header |
| dequant_round    | from model header |
| dequant_zp       | from model header |

```c
static void dequantize_output(const int8_t *src, float *dst, size_t len,
                              const nrf_axon_nn_compiled_model_s *model)
{
    const uint32_t deq_mult  = model->output_dequant_mult;
    const uint8_t  deq_round = model->output_dequant_round;
    const int8_t   deq_zp    = model->output_dequant_zp;

    for (size_t i = 0; i < len; i++) {
        dst[i] = (src[i] - deq_zp) * ((float)deq_mult / (1 << deq_round));
    }
}
```

## Memory Requirements

| Buffer                  | Size (bytes) |
|-------------------------|--------------|
| Input buffer            | 150          |
| Output buffer           | 7 (padded to 8 by Axon) |
| Interlayer buffer       | 408 (min)    |
| PSUM buffer             | 0            |
| Model constants (flash) | 12284        |
| Command buffer (flash)  | 3552         |

Make sure `CONFIG_NRF_AXON_INTERLAYER_BUFFER_SIZE` is at least **408**.
