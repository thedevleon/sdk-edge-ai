#
# Copyright (c) 2026 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: LicenseRef-Nordic-5-Clause
#

"""
Activity Detection TFLite Model for Axon NPU
=============================================

Trains a 7-class human activity recognition model using the PAMAP2 dataset
(100 Hz triaxial accelerometer from the hand/wrist IMU, ±16g scale).

Target classes mapped from PAMAP2 activity IDs:
  1=lying -> lying_down, 2=sitting, 3=standing, 4=walking,
  5=running, 6=cycling, 24=rope_jumping -> workout

Output: int8-quantized TFLite model suitable for the Axon NPU compiler.
"""

import os
import glob
import numpy as np
import tensorflow as tf
from pathlib import Path

SEED = 42
tf.random.set_seed(SEED)
np.random.seed(SEED)

# ── Model / data parameters ─────────────────────────────────────────
WINDOW_SIZE = 50          # samples per inference window (0.5 s @ 100 Hz)
NUM_AXES = 3              # accel x, y, z
NUM_FEATURES = WINDOW_SIZE * NUM_AXES
NUM_CLASSES = 7
SAMPLE_RATE_HZ = 100      # PAMAP2 IMU sample rate

CLASS_NAMES = [
    "sitting",       # 0  <- PAMAP2 activity 2
    "standing",      # 1  <- PAMAP2 activity 3
    "lying_down",    # 2  <- PAMAP2 activity 1
    "walking",       # 3  <- PAMAP2 activity 4
    "running",       # 4  <- PAMAP2 activity 5
    "cycling",       # 5  <- PAMAP2 activity 6
    "workout",       # 6  <- PAMAP2 activity 24 (rope jumping)
]

# PAMAP2 activity ID -> our class index
ACTIVITY_MAP = {
    2:  0,   # sitting
    3:  1,   # standing
    1:  2,   # lying_down
    4:  3,   # walking
    5:  4,   # running
    6:  5,   # cycling
    24: 6,   # workout (rope jumping)
}

# PAMAP2 column indices (0-based)
COL_ACT_ID = 1
COL_HAND_ACCEL = (4, 5, 6)  # hand IMU ±16g accel x, y, z

DATASET_URL = "https://archive.ics.uci.edu/static/public/231/pamap2+physical+activity+monitoring.zip"

OUTPUT_DIR = Path("output/")

# ── Data loading and windowing ───────────────────────────────────────

def load_subject(filepath: Path) -> np.ndarray:
    """Load one subject .dat file. Returns (N, 54) float32 array with NaNs."""
    data = np.loadtxt(filepath, dtype=np.float32, comments=None)
    # Replace NaN with 0 for robustness
    data = np.nan_to_num(data, nan=0.0)
    return data


def extract_windows(data: np.ndarray, window_size: int, stride: int):
    """Extract overlapping windows from one subject's data.

    Returns (windows, labels) where each window is flattened
    (window_size * NUM_AXES,) float32 accel-only.
    """
    windows = []
    labels = []

    act_ids = data[:, COL_ACT_ID].astype(int)
    accel = data[:, list(COL_HAND_ACCEL)]  # (N, 3)

    # Walk through by activity segment to avoid crossing boundaries
    i = 0
    while i < len(act_ids):
        act = act_ids[i]
        if act not in ACTIVITY_MAP:
            i += 1
            continue

        # Find end of this contiguous activity segment
        j = i
        while j < len(act_ids) and act_ids[j] == act:
            j += 1

        # Extract windows from this segment
        seg = accel[i:j]
        start = 0
        while start + window_size <= len(seg):
            win = seg[start:start + window_size].flatten()
            windows.append(win)
            labels.append(ACTIVITY_MAP[act])
            start += stride

        i = j

    return np.array(windows, dtype=np.float32), np.array(labels, dtype=np.int64)


def load_all_data(window_size: int = WINDOW_SIZE, stride: int = 25):
    """Load all subjects from Protocol and Optional, extract windows."""
    x_list, y_list = [], []

    for file in glob.glob("data/PAMAP2_Dataset/Protocol/subject*.dat"):
        print(f"\n  Loading from {file}")
        data = load_subject(file)
        w, l = extract_windows(data, window_size, stride)
        x_list.append(w)
        y_list.append(l)
        print(f"  {len(l)} windows")

        # print(f"\n  Loading from {data_dir.name}/")
        # for fp in dat_files:
        #     print(f"    {fp.name} ...", end="")
        #     data = load_subject(fp)
        #     w, l = extract_windows(data, window_size, stride)
        #     x_list.append(w)
        #     y_list.append(l)
        #     print(f"  {len(l)} windows")

    if not x_list:
        raise FileNotFoundError(
            f"No subject*.dat files found."
        )

    return np.concatenate(x_list), np.concatenate(y_list)


def make_representative_dataset(x: np.ndarray):
    """Return a callable yielding the first 100 real samples"""
    calibration_data = x[:100].astype(np.int8)

    def representative_dataset():
        for i in range(len(calibration_data)):
            yield [calibration_data[i:i + 1]]
        return representative_dataset

# ── Keras model ──────────────────────────────────────────────────────

def build_model() -> tf.keras.Model:
    """Dense-only model compatible with Axon NPU (FullyConnected + ReLU)."""
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, input_dim=NUM_FEATURES, activation='relu', name='dense_0'),
        tf.keras.layers.Dense(32, activation='relu', name='dense_1'),
        tf.keras.layers.Dense(NUM_CLASSES, activation='linear', name='output'),
    ], name="activity_detection")
    return model

# ── Main ─────────────────────────────────────────────────────────────

def main():
    os.makedirs(os.path.dirname("output/"), exist_ok=True)

    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        print(f"GPU devices: {gpus}")
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    else:
        print("No GPU detected, using CPU")

    # ── Load and window data ─────────────────────────────────────────
    print("\nLoading PAMAP2 dataset ...")
    x_all, y_all = load_all_data(window_size=WINDOW_SIZE, stride=25)
    print(f"  total windows: {len(y_all)}")

    unique, counts = np.unique(y_all, return_counts=True)
    print("  class distribution:")
    for cls_id, cnt in zip(unique, counts):
        print(f"    {CLASS_NAMES[cls_id]:15s}: {cnt:6d}")

    # ── Shuffle and split ────────────────────────────────────────────
    indices = np.arange(len(y_all))
    np.random.shuffle(indices)
    x_all, y_all = x_all[indices], y_all[indices]

    split = int(0.8 * len(y_all))
    x_train, y_train = x_all[:split], y_all[:split]
    x_test, y_test = x_all[split:], y_all[split:]

    print(f"\n  train: {x_train.shape}  test: {x_test.shape}")

    # ── Train float model ────────────────────────────────────────────
    model = build_model()
    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )
    model.summary()

    print("\nTraining ...")
    model.fit(x_train, y_train, epochs=30, batch_size=64,
              validation_split=0.1, verbose=2)

    loss, acc = model.evaluate(x_test, y_test, verbose=0)
    print(f"\nFloat model - test accuracy: {acc:.4f}  loss: {loss:.4f}")

    # ── Convert to int8-quantized TFLite ─────────────────────────────
    print("\nConverting to int8-quantized TFLite ...")

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    # converter.optimizations = [tf.lite.Optimize.DEFAULT]
    # converter.representative_dataset = make_representative_dataset(x_train)
    # converter.target_spec.supported_ops = [
    #     tf.lite.OpsSet.TFLITE_BUILTINS_INT8,
    # ]
    # converter.inference_input_type = tf.int8
    # converter.inference_output_type = tf.int8

    tflite_model = converter.convert()

    # Print the signatures from the converted model
    interpreter = tf.lite.Interpreter(model_content=tflite_model)

    signatures = interpreter.get_signature_list()
    print(signatures)

    tflite_path = OUTPUT_DIR / "activity_model.tflite"
    tflite_path.write_bytes(tflite_model)
    print(f"  saved -> {tflite_path}  ({len(tflite_model)} bytes)")

    # ── Verify with TFLite interpreter ───────────────────────────────
    print("\nVerifying quantized model ...")
    interp = tf.lite.Interpreter(model_path=str(tflite_path))
    interp.allocate_tensors()

    inp_det = interp.get_input_details()[0]
    out_det = interp.get_output_details()[0]

    q_scale_in = inp_det["quantization_parameters"]["scales"][0]
    q_zp_in = inp_det["quantization_parameters"]["zero_points"][0]
    q_scale_out = out_det["quantization_parameters"]["scales"][0]
    q_zp_out = out_det["quantization_parameters"]["zero_points"][0]

    print(f"  input:  scale={q_scale_in:.6f}  zp={q_zp_in}  shape={inp_det['shape']}")
    print(f"  output: scale={q_scale_out:.6f}  zp={q_zp_out}  shape={out_det['shape']}")

    correct = 0
    n_verify = min(500, len(x_test))
    per_class_correct = np.zeros(NUM_CLASSES, dtype=int)
    per_class_total = np.zeros(NUM_CLASSES, dtype=int)

    for i in range(n_verify):
        f32_sample = x_test[i:i + 1]
        q_input = np.round(f32_sample / q_scale_in + q_zp_in).astype(np.int8)
        interp.set_tensor(inp_det["index"], q_input)
        interp.invoke()
        q_output = interp.get_tensor(out_det["index"])
        predicted = np.argmax(q_output.flatten())
        actual = y_test[i]
        per_class_total[actual] += 1
        if predicted == actual:
            correct += 1
            per_class_correct[actual] += 1

    print(f"  quantized accuracy on {n_verify} test samples: {correct / n_verify:.4f}")
    print("  per-class accuracy:")
    for cls_id in range(NUM_CLASSES):
        if per_class_total[cls_id] > 0:
            ca = per_class_correct[cls_id] / per_class_total[cls_id]
            print(f"    {CLASS_NAMES[cls_id]:15s}: {ca:.4f}  ({per_class_correct[cls_id]}/{per_class_total[cls_id]})")

    # ── Save metadata for Axon compiler ──────────────────────────────
    meta_path = OUTPUT_DIR / "activity_model_meta.txt"
    with open(meta_path, "w") as f:
        f.write(f"model_name: ACTIVITY_MODEL\n")
        f.write(f"dataset: PAMAP2\n")
        f.write(f"window_size: {WINDOW_SIZE}\n")
        f.write(f"num_axes: {NUM_AXES}\n")
        f.write(f"num_classes: {NUM_CLASSES}\n")
        f.write(f"classes: {','.join(CLASS_NAMES)}\n")
        f.write(f"sample_rate_hz: {SAMPLE_RATE_HZ}\n")
        f.write(f"imu_position: hand_wrist\n")
        f.write(f"accel_scale: plusminus_16g\n")
        f.write(f"input_quant_scale: {q_scale_in}\n")
        f.write(f"input_quant_zp: {q_zp_in}\n")
        f.write(f"output_quant_scale: {q_scale_out}\n")
        f.write(f"output_quant_zp: {q_zp_out}\n")

    print(f"\n  saved -> {meta_path}")
    print("Done.")


if __name__ == "__main__":
    main()
