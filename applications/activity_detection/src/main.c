/*
 * Copyright (c) 2026 Nordic Semiconductor ASA
 *
 * SPDX-License-Identifier: LicenseRef-Nordic-5-Clause
 *
 * Activity Detection application
 *
 * Reads triaxial accelerometer data from a LIS2DUX12 on I2C at 100 Hz,
 * collects a 50-sample window (x, y, z interleaved), quantizes to int8,
 * and runs inference on the Axon NPU.  Prints the detected activity.
 */

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/sensor.h>
#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>

#include <axon/nrf_axon_platform.h>
#include <drivers/axon/nrf_axon_driver.h>
#include <drivers/axon/nrf_axon_nn_infer.h>

#include "nrf_axon_model_activity_detection.h"

LOG_MODULE_REGISTER(activity, LOG_LEVEL_INF);

/* ── Activity labels (must match training order) ──────────────────── */

enum activity_class {
	SITTING    = 0,
	STANDING   = 1,
	LYING_DOWN = 2,
	WALKING    = 3,
	RUNNING    = 4,
	CYCLING    = 5,
	WORKOUT    = 6,
};

static const char *const ACTIVITY_LABELS[] = {
	[SITTING]     = "Sitting",
	[STANDING]    = "Standing",
	[LYING_DOWN]  = "Lying down",
	[WALKING]     = "Walking",
	[RUNNING]     = "Running",
	[CYCLING]     = "Cycling",
	[WORKOUT]     = "Workout",
};

#define NUM_ACTIVITIES (sizeof(ACTIVITY_LABELS) / sizeof(ACTIVITY_LABELS[0]))

/* ── Model constants ──────────────────────────────────────────────── */

#define WINDOW_SIZE  50
#define NUM_AXES     3
#define NUM_FEATURES (WINDOW_SIZE * NUM_AXES)
#define SENSOR_ODR_HZ 100
#define SAMPLE_INTERVAL_MS (1000 / SENSOR_ODR_HZ)

/* ── LIS2DUX12 sensor ─────────────────────────────────────────────── */

static const struct device *const accel_dev =
	DEVICE_DT_GET_ONE(st_lis2dux12);

/* ── Quantization helpers ─────────────────────────────────────────── */

/*
 * Quantization:  q8 = (float_val / scale) + zp
 * Dequantization: float_val = (q8 - zp) * scale
 *
 * These parameters come from the TFLite model and are embedded in
 * the compiled model header's input/output descriptors.
 */

static void quantize_window(const float *src, int8_t *dst, size_t len,
			    const nrf_axon_nn_compiled_model_input_s *input)
{
	const uint32_t q_mult = input->quant_mult;
	const uint8_t q_round = input->quant_round;
	const int8_t q_zp = input->quant_zp;

	for (size_t i = 0; i < len; i++) {
		dst[i] = (int8_t)((uint32_t)(src[i] * q_mult) >> q_round) + q_zp;
	}
}

static void dequantize_output(const int8_t *src, float *dst, size_t len,
			      const nrf_axon_nn_compiled_model_s *model)
{
	const uint32_t deq_mult = model->output_dequant_mult;
	const uint8_t deq_round = model->output_dequant_round;
	const int8_t deq_zp = model->output_dequant_zp;

	for (size_t i = 0; i < len; i++) {
		dst[i] = (src[i] - deq_zp) * ((float)deq_mult / (1 << deq_round));
	}
}

/* ── Accelerometer sample collection ──────────────────────────────── */

/*
 * Read one sample from the LIS2DUX12 and convert to m/s^2.
 * Returns 0 on success.
 */
static int read_accel_sample(float xyz[3])
{
	int ret;

	ret = sensor_sample_fetch(accel_dev);
	if (ret < 0) {
		return ret;
	}

	struct sensor_value val;

	ret = sensor_channel_get(accel_dev, SENSOR_CHAN_ACCEL_X, &val);
	if (ret < 0) {
		return ret;
	}
	xyz[0] = (float)sensor_value_to_double(&val);

	ret = sensor_channel_get(accel_dev, SENSOR_CHAN_ACCEL_Y, &val);
	if (ret < 0) {
		return ret;
	}
	xyz[1] = (float)sensor_value_to_double(&val);

	ret = sensor_channel_get(accel_dev, SENSOR_CHAN_ACCEL_Z, &val);
	if (ret < 0) {
		return ret;
	}
	xyz[2] = (float)sensor_value_to_double(&val);

	return 0;
}

/*
 * Collect WINDOW_SIZE samples at SENSOR_ODR_HZ, interleaving x, y, z
 * into a flat array: [x0, y0, z0, x1, y1, z1, ..., xN, yN, zN]
 *
 * This matches the flattening used during training (each window row
 * was [x, y, z] flattened to row-major order).
 */
static int collect_window(float *window)
{
	for (int s = 0; s < WINDOW_SIZE; s++) {
		float xyz[3];
		int ret;

		ret = read_accel_sample(xyz);
		if (ret < 0) {
			LOG_ERR("Sensor read failed: %d", ret);
			return ret;
		}

		window[s * NUM_AXES + 0] = xyz[0];
		window[s * NUM_AXES + 1] = xyz[1];
		window[s * NUM_AXES + 2] = xyz[2];

		if (IS_ENABLED(CONFIG_ACTIVITY_PRINT_RAW_ACCEL)) {
			LOG_INF("[%d] a=%.2f %.2f %.2f", s,
				(double)xyz[0], (double)xyz[1], (double)xyz[2]);
		}

		/* Wait for next sample period */
		k_msleep(SAMPLE_INTERVAL_MS);
	}

	return 0;
}

/* ── Main ──────────────────────────────────────────────────────────── */

int main(void)
{
	int ret;
	nrf_axon_result_e result;

	/* ── Init LIS2DUX12 ────────────────────────────────────────── */
	if (!device_is_ready(accel_dev)) {
		LOG_ERR("LIS2DUX12 not ready");
		return -1;
	}
	LOG_INF("LIS2DUX12 initialized");

	/* ── Init Axon NPU ─────────────────────────────────────────── */
	result = nrf_axon_platform_init();
	if (result != NRF_AXON_RESULT_SUCCESS) {
		LOG_ERR("Axon platform init failed: %d", result);
		return -1;
	}
	LOG_INF("Axon NPU initialized");

	/* ── Validate compiled model ───────────────────────────────── */
	result = nrf_axon_nn_model_validate(&model_ACTIVITY_MODEL);
	if (result != NRF_AXON_RESULT_SUCCESS) {
		LOG_ERR("Model validation failed: %d", result);
		LOG_ERR("Check that the Axon-compiled model header is correct "
			"and CONFIG_NRF_AXON_INTERLAYER_BUFFER_SIZE is large enough.");
		return -1;
	}

	/* Init persistent vars (harmless for non-streaming models) */
	ret = nrf_axon_nn_model_init_vars(&model_ACTIVITY_MODEL);
	if (ret < 0) {
		LOG_ERR("Model persistent vars init failed: %d", ret);
		return -1;
	}

	const nrf_axon_nn_compiled_model_input_s *model_input =
		&model_ACTIVITY_MODEL.inputs[model_ACTIVITY_MODEL.external_input_ndx];

	LOG_INF("Model \"%s\" loaded", model_ACTIVITY_MODEL.model_name);
	LOG_INF("  input:  %dx%dx%d  byte_width=%d",
		model_input->dimensions.height,
		model_input->dimensions.width,
		model_input->dimensions.channel_cnt,
		model_input->dimensions.byte_width);
	LOG_INF("  output: %dx%dx%d  byte_width=%d",
		model_ACTIVITY_MODEL.output_dimensions.height,
		model_ACTIVITY_MODEL.output_dimensions.width,
		model_ACTIVITY_MODEL.output_dimensions.channel_cnt,
		model_ACTIVITY_MODEL.output_dimensions.byte_width);
	LOG_INF("  classes: %zu", NUM_ACTIVITIES);

	/* ── Allocate buffers ──────────────────────────────────────── */
	/*
	 * Input window in float (from sensor), quantized int8 buffer
	 * for Axon, and output buffer sized for packed output.
	 */
	static float window_float[NUM_FEATURES];
	static int8_t input_q8[NUM_FEATURES];

	/* Packed output: output dimensions rounded up to 4-byte boundary */
	const uint16_t out_bytes = model_ACTIVITY_MODEL.output_dimensions.width *
				  model_ACTIVITY_MODEL.output_dimensions.channel_cnt *
				  model_ACTIVITY_MODEL.output_dimensions.height *
				  model_ACTIVITY_MODEL.output_dimensions.byte_width;
	static int8_t output_q8[64];  /* generous for 7-class output */

	LOG_INF("Activity Detection: initialized");
	LOG_INF("Activity Detection: running");

	/* ── Main inference loop ───────────────────────────────────── */
	while (1) {
		/* 1. Collect a full window of accelerometer data */
		ret = collect_window(window_float);
		if (ret < 0) {
			LOG_WRN("Skipping window due to sensor error");
			k_msleep(100);
			continue;
		}

		/* 2. Quantize float -> int8 using model's input parameters */
		quantize_window(window_float, input_q8, NUM_FEATURES, model_input);

		/* 3. Run synchronous inference on Axon NPU */
		result = nrf_axon_nn_model_infer_sync(&model_ACTIVITY_MODEL,
						      input_q8, output_q8);
		if (result != NRF_AXON_RESULT_SUCCESS) {
			LOG_ERR("Inference failed: %d", result);
			continue;
		}

		/* 4. Get classification result */
		int32_t score;
		int16_t class_idx = nrf_axon_nn_get_classification(
			&model_ACTIVITY_MODEL, output_q8, NULL, &score);

		if (class_idx >= 0 && class_idx < (int16_t)NUM_ACTIVITIES) {
			/*
			 * Dequantize all outputs to get per-class confidence.
			 * For a classification model, the output logits can be
			 * soft-maxed externally if probability estimates are
			 * needed.  Here we report the argmax and its raw score.
			 */
			float logits[NUM_ACTIVITIES];

			dequantize_output(output_q8, logits, NUM_ACTIVITIES,
					  &model_ACTIVITY_MODEL);

			LOG_INF(">> %s  (class %d, score %d)",
				ACTIVITY_LABELS[class_idx], class_idx, score);

			if (IS_ENABLED(CONFIG_LOG)) {
				/* Log all class logits for debugging */
				char logbuf[128];
				int pos = 0;

				for (int i = 0; i < (int)NUM_ACTIVITIES && pos < 100; i++) {
					pos += snprintf(logbuf + pos,
							sizeof(logbuf) - pos,
							"%s%.1f ",
							ACTIVITY_LABELS[i], (double)logits[i]);
				}
				LOG_DBG("  logits: %s", logbuf);
			}
		} else {
			LOG_WRN("Classification returned invalid index: %d", class_idx);
		}

		/*
		 * Optional extra sleep between windows to throttle inference
		 * rate.  At 100 Hz ODR + 50-sample window the collection
		 * already takes ~500 ms, so this is only needed if you want
		 * a gap between windows.
		 */
		if (CONFIG_ACTIVITY_INFERENCE_INTERVAL_MS > (WINDOW_SIZE * SAMPLE_INTERVAL_MS)) {
			k_msleep(CONFIG_ACTIVITY_INFERENCE_INTERVAL_MS -
				 WINDOW_SIZE * SAMPLE_INTERVAL_MS);
		}
	}

	return 0;
}
