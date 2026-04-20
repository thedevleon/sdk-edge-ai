/*
 * Copyright (c) 2026 Nordic Semiconductor ASA
 *
 * SPDX-License-Identifier: LicenseRef-Nordic-5-Clause
 *
 * Placeholder compiled model header.
 *
 * Replace this file with the output of the Axon compiler:
 *   ./run.sh compile
 *
 * The real header defines:
 *   - model_ACTIVITY_MODEL  (nrf_axon_nn_compiled_model_s)
 *   - axon_model_const_ACTIVITY_MODEL (weights & biases)
 *   - cmd_buffer_ACTIVITY_MODEL[] (Axon command buffer)
 *   - NRF_AXON_MODEL_ACTIVITY_MODEL_MAX_IL_BUFFER_USED
 */
#pragma once

/*
 * This placeholder allows the application to compile before the model
 * is compiled. It defines a minimal model that will fail validation
 * at runtime. Replace with the real compiled header.
 */

#include <drivers/axon/nrf_axon_nn_infer.h>

#define NRF_AXON_MODEL_ACTIVITY_MODEL_MAX_IL_BUFFER_USED 0

extern const nrf_axon_nn_compiled_model_s model_ACTIVITY_MODEL;
