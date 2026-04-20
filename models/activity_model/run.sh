#!/bin/bash
#
# Copyright (c) 2026 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: LicenseRef-Nordic-5-Clause
#

# ── Train + Compile activity model ──────────────────────────────────
# Usage:
#   ./run.sh train          # download PAMAP2 + train model, produce TFLite
#   ./run.sh compile        # compile TFLite for Axon NPU
#   ./run.sh all            # train + compile
#
# This script runs inside the ROCm docker container or locally with
# tensorflow + numpy installed.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AXON_COMPILER_DIR="/workspace/tools/axon/compiler"

train() {
    echo "=== Training activity detection model (PAMAP2) ==="
    python3 "$SCRIPT_DIR/train_model.py"
}

compile() {
    echo "=== Compiling TFLite model for Axon NPU ==="

    if [ ! -f "$SCRIPT_DIR/output/activity_model.tflite" ]; then
        echo "ERROR: output/activity_model.tflite not found. Run 'train' first."
        exit 1
    fi

    if [ ! -d "$AXON_COMPILER_DIR" ]; then
        echo "ERROR: Axon compiler not found at $AXON_COMPILER_DIR"
        echo "       Run this from within the docker container or adjust AXON_COMPILER_DIR."
        exit 1
    fi

    cd "$AXON_COMPILER_DIR/scripts"
    python3 axons_ml_nn_compiler_executor.py "$SCRIPT_DIR/compiler_input.yaml"

    # Copy generated header into the Zephyr application
    OUTPUT_HEADER="outputs/nrf_axon_model_ACTIVITY_MODEL.h"
    APP_GEN_DIR="$SCRIPT_DIR/../../applications/activity_detection/src/generated"

    if [ -f "$OUTPUT_HEADER" ]; then
        mkdir -p "$APP_GEN_DIR"
        cp "$OUTPUT_HEADER" "$APP_GEN_DIR/nrf_axon_model_activity_detection.h"
        echo "  copied -> $APP_GEN_DIR/nrf_axon_model_activity_detection.h"
    else
        echo "WARNING: Expected output not found at $OUTPUT_HEADER"
        echo "Check $AXON_COMPILER_DIR/scripts/outputs/ for generated files."
    fi
}

case "${1:-all}" in
    train)   train ;;
    compile) compile ;;
    all)     train && compile ;;
    *)
        echo "Usage: $0 {train|compile|all}"
        exit 1
        ;;
esac
