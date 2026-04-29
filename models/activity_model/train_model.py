#
# Copyright (c) 2026 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: LicenseRef-Nordic-5-Clause
#

"""
Activity Detection TFLite Model for Axon NPU
=============================================

Trains a 10-class human activity recognition model using the Capture24 dataset
(100 Hz triaxial accelerometer from wrist-worn Axivity AX3, ±8g scale).

Uses WillettsSpecific2018 labels directly:
  bicycling, household-chores, manual-work, mixed-activity,
  sitting, sleep, sports, standing, vehicle, walking

Output: int8-quantized TFLite model suitable for the Axon NPU compiler.
"""

import os
import time
import glob
import numpy as np
import pandas as pd
import tensorflow as tf
from pathlib import Path
from sklearn.utils.class_weight import compute_class_weight
from sklearn.model_selection import StratifiedShuffleSplit, train_test_split
from sklearn.metrics import confusion_matrix, classification_report

try:
    import tensorflow_model_optimization as tfmot
    TFMOT_AVAILABLE = True
except ImportError:
    TFMOT_AVAILABLE = False

from model import build_model, SELECTED_MODEL, MODEL_REGISTRY

SEED = 42
tf.random.set_seed(SEED)
np.random.seed(SEED)

# ── Model / data parameters ─────────────────────────────────────────
WINDOW_SIZE = 50          # samples per inference window (0.5 s @ 100 Hz)
NUM_AXES = 3              # accel x, y, z
NUM_FEATURES = WINDOW_SIZE * NUM_AXES
NUM_CLASSES = 10
SAMPLE_RATE_HZ = 100      # Capture24 IMU sample rate

EPOCHS = 20
BATCH_SIZE = 128
AUGMENT_FACTOR = 2        # number of augmented copies to generate
USE_QAT = True            # enable Quantization-Aware Training fine-tuning
QAT_EPOCHS = 5

CLASS_NAMES = [
    "bicycling",         # 0
    "household-chores",  # 1
    "manual-work",       # 2
    "mixed-activity",    # 3
    "sitting",           # 4
    "sleep",             # 5
    "sports",            # 6
    "standing",          # 7
    "vehicle",           # 8
    "walking",           # 9
]

# ── Capture24 annotation configuration ───────────────────────────────
ANNOTATION_SCHEME = "label:WillettsSpecific2018"

DATA_DIR = Path("data/capture24")
OUTPUT_DIR = Path("models")

# Set to an int to limit the number of subjects loaded (None = all).
MAX_SUBJECTS = 20

# ── Data loading and windowing ───────────────────────────────────────


def load_annotation_label_map(dict_path: Path, scheme: str) -> dict:
    """Load annotation-label-dictionary.csv.

    Returns a dict mapping raw annotation text -> class index,
    using scheme labels directly (auto-indexed from CLASS_NAMES).
    """
    df = pd.read_csv(dict_path)
    label_to_idx = {name: i for i, name in enumerate(CLASS_NAMES)}
    df["class_idx"] = df[scheme].map(label_to_idx)
    df = df.dropna(subset=["class_idx"])
    return dict(zip(df["annotation"], df["class_idx"].astype(int)))


def extract_windows(accel: np.ndarray, class_ids: np.ndarray,
                    window_size: int, stride: int):
    """Extract overlapping windows from one subject's data.

    Windows never cross activity segment boundaries.

    Returns (windows, labels) where each window has shape
    (window_size, NUM_AXES) float32.
    """
    changes = np.where(class_ids[:-1] != class_ids[1:])[0] + 1
    segments = np.split(np.arange(len(class_ids)), changes)

    windows = []
    labels = []

    for seg_indices in segments:
        if len(seg_indices) < window_size:
            continue
        label = class_ids[seg_indices[0]]
        seg_accel = accel[seg_indices]

        start = 0
        while start + window_size <= len(seg_accel):
            win = seg_accel[start:start + window_size]
            windows.append(win)
            labels.append(label)
            start += stride

    if not windows:
        return (np.empty((0, window_size, NUM_AXES), dtype=np.float32),
                np.empty(0, dtype=np.int32))

    return np.array(windows, dtype=np.float32), np.array(labels, dtype=np.int32)


def load_all_data(window_size: int = WINDOW_SIZE, stride: int = 25,
                  test_subject_ratio: float = 0.2):
    """Load all subjects from Capture24, extract windows, split by subject.

    Subject-wise split prevents data leakage (windows from the same
    subject never appear in both train and test).
    """
    dict_path = DATA_DIR / "annotation-label-dictionary.csv"
    ann_to_class = load_annotation_label_map(dict_path, ANNOTATION_SCHEME)

    subject_files = sorted(glob.glob(str(DATA_DIR / "P*.csv.gz")))

    if not subject_files:
        raise FileNotFoundError(
            f"No P*.csv.gz files found in {DATA_DIR}"
        )

    if MAX_SUBJECTS is not None:
        subject_files = subject_files[:MAX_SUBJECTS]

    # Subject-wise split to prevent data leakage
    rng = np.random.RandomState(SEED)
    rng.shuffle(subject_files)
    n_test = max(1, int(len(subject_files) * test_subject_ratio))
    test_files = subject_files[:n_test]
    train_files = subject_files[n_test:]

    def _load_files(files):
        x_list, y_list = [], []
        for file in files:
            name = Path(file).name
            print(f"\n  Loading {name} ...", end="")
            df = pd.read_csv(file)[["x", "y", "z", "annotation"]]

            class_ids = df["annotation"].map(ann_to_class)
            valid = class_ids.notna()

            if valid.sum() == 0:
                print(" no valid annotations, skipping")
                continue

            accel = df.loc[valid, ["x", "y", "z"]].values.astype(np.float32)
            ids = class_ids[valid].values.astype(np.int32)

            w, l = extract_windows(accel, ids, window_size, stride)

            if len(l) > 0:
                x_list.append(w)
                y_list.append(l)
                print(f"  {len(l)} windows")
            else:
                print(" no windows extracted")

        if not x_list:
            return (np.empty((0, window_size, NUM_AXES), dtype=np.float32),
                    np.empty(0, dtype=np.int32))

        return np.concatenate(x_list), np.concatenate(y_list)

    x_train, y_train = _load_files(train_files)
    x_test, y_test = _load_files(test_files)
    return x_train, y_train, x_test, y_test


def augment_windows(windows: np.ndarray, labels: np.ndarray, factor: int = 1):
    """Apply time-series augmentation to training windows.

    Augmentations (from tiny benchmark audio/image pipelines, adapted
    for 1-D triaxial accelerometer time-series):
      - Gaussian noise
      - Random magnitude scaling
      - Random time shift (circular)
    """
    if factor <= 0:
        return windows, labels

    aug_windows = []
    aug_labels = []
    for _ in range(factor):
        for w, l in zip(windows, labels):
            aug = w.copy()
            # Gaussian noise
            aug += np.random.normal(0.0, 0.01, aug.shape).astype(np.float32)
            # Random magnitude scaling
            scale = np.random.uniform(0.9, 1.1)
            aug *= scale
            # Random time shift (circular)
            shift = np.random.randint(-3, 4)
            if shift != 0:
                aug = np.roll(aug, shift, axis=0)
            aug_windows.append(aug)
            aug_labels.append(l)

    aug_windows = np.array(aug_windows, dtype=np.float32)
    aug_labels = np.array(aug_labels, dtype=np.int32)
    return np.concatenate([windows, aug_windows]), np.concatenate([labels, aug_labels])


def lr_schedule(epoch):
    """Step-decay learning rate schedule (adapted from tiny KWS benchmark)."""
    if epoch < 10:
        return 0.001
    elif epoch < 15:
        return 0.0005
    elif epoch < 18:
        return 0.0001
    else:
        return 0.00005


def make_stratified_calibration(x: np.ndarray, y: np.ndarray, n_samples: int = 200):
    """Create a stratified calibration set for TFLite int8 quantization."""
    if len(x) <= n_samples:
        return x
    try:
        sss = StratifiedShuffleSplit(n_splits=1, test_size=n_samples, random_state=SEED)
        _, cal_idx = next(sss.split(x, y))
        return x[cal_idx]
    except ValueError:
        # fallback: random subset if stratification fails
        rng = np.random.RandomState(SEED)
        idx = rng.choice(len(x), size=n_samples, replace=False)
        return x[idx]


def make_representative_dataset(calibration_data: np.ndarray):
    """Return a callable yielding samples for TFLite int8 calibration."""
    def rep_dataset():
        for i in range(len(calibration_data)):
            yield [calibration_data[i:i + 1]]
    return rep_dataset


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
    print("\nLoading Capture24 dataset ...")
    x_train, y_train, x_test, y_test = load_all_data(
        window_size=WINDOW_SIZE, stride=25, test_subject_ratio=0.2
    )
    print(f"\n  total train windows: {len(y_train)}")
    print(f"  total test windows:  {len(y_test)}")

    unique, counts = np.unique(y_train, return_counts=True)
    print("  train class distribution:")
    for cls_id, cnt in zip(unique, counts):
        print(f"    {CLASS_NAMES[cls_id]:15s}: {cnt:6d}")

    # ── Stratified train/validation split ────────────────────────────
    print("\nStratified train/validation split ...")
    try:
        x_train, x_val, y_train, y_val = train_test_split(
            x_train, y_train, test_size=0.1, random_state=SEED, stratify=y_train
        )
    except ValueError:
        print("  stratified split failed (too few samples per class), using random split")
        x_train, x_val, y_train, y_val = train_test_split(
            x_train, y_train, test_size=0.1, random_state=SEED
        )
    print(f"  train: {len(y_train)}  val: {len(y_val)}")

    # ── Data augmentation (train only) ───────────────────────────────
    if AUGMENT_FACTOR > 0:
        print(f"\nAugmenting training data (factor={AUGMENT_FACTOR}) ...")
        x_train, y_train = augment_windows(x_train, y_train, factor=AUGMENT_FACTOR)
        print(f"  augmented train size: {len(y_train)}")

    # ── Normalize to [-1, 1] (global, computed on train) ────────────
    input_scale = np.max(np.abs(x_train))
    x_train = x_train / input_scale
    x_val = x_val / input_scale
    x_test = x_test / input_scale
    print(f"\n  input scale factor: {input_scale:.4f}")

    print(f"\n  train: {x_train.shape}  val: {x_val.shape}  test: {x_test.shape}")

    # ── Class weights for imbalance ───────────────────────────────────
    class_weights = compute_class_weight(
        'balanced', classes=np.unique(y_train), y=y_train
    )
    class_weight_dict = {i: w for i, w in enumerate(class_weights)}
    print("\n  class weights (raw):")
    for cls_id, w in class_weight_dict.items():
        print(f"    {CLASS_NAMES[cls_id]:15s}: {w:.3f}")

    # Clamp to prevent extreme minority-class domination
    MAX_CLASS_WEIGHT = 10.0
    class_weight_dict = {i: min(w, MAX_CLASS_WEIGHT) for i, w in class_weight_dict.items()}
    print(f"  class weights (clamped at {MAX_CLASS_WEIGHT}):")
    for cls_id, w in class_weight_dict.items():
        print(f"    {CLASS_NAMES[cls_id]:15s}: {w:.3f}")

    # ── Train float model ────────────────────────────────────────────
    print(f"\nSelected model: {SELECTED_MODEL}")
    print(f"Available models: {list(MODEL_REGISTRY.keys())}")
    model = build_model(SELECTED_MODEL,
                        window_size=WINDOW_SIZE,
                        num_axes=NUM_AXES,
                        num_classes=NUM_CLASSES)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )
    model.summary()

    print("\nTraining float model ...")
    total_start = time.time()
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_accuracy', patience=5, mode='max',
            restore_best_weights=True, verbose=1,
        ),
        tf.keras.callbacks.LearningRateScheduler(lr_schedule, verbose=1),
        tf.keras.callbacks.ModelCheckpoint(
            str(OUTPUT_DIR / "activity_model_best.keras"),
            monitor='val_accuracy', mode='max',
            save_best_only=True, verbose=1,
        ),
    ]
    model.fit(x_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE,
              validation_data=(x_val, y_val), verbose=1, callbacks=callbacks,
              class_weight=class_weight_dict)
    total_duration = time.time() - total_start
    print(f"\nTotal training time: {total_duration:.1f}s ({total_duration/60:.1f}min)")

    loss, acc = model.evaluate(x_test, y_test, verbose=0)
    print(f"\nFloat model - test accuracy: {acc:.4f}  loss: {loss:.4f}")

    # ── Quantization-Aware Training fine-tuning ──────────────────────
    if USE_QAT and TFMOT_AVAILABLE:
        print("\n--- QAT fine-tuning ---")
        qat_model = tfmot.quantization.keras.quantize_model(model)
        qat_model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=["accuracy"],
        )
        qat_model.fit(x_train, y_train, epochs=QAT_EPOCHS, batch_size=BATCH_SIZE,
                      validation_data=(x_val, y_val), verbose=1,
                      class_weight=class_weight_dict)
        model = qat_model
        loss, acc = model.evaluate(x_test, y_test, verbose=0)
        print(f"\nAfter QAT - test accuracy: {acc:.4f}  loss: {loss:.4f}")
    elif USE_QAT and not TFMOT_AVAILABLE:
        print("\nQAT requested but tensorflow-model-optimization not installed. Skipping.")

    # --- Save model ---
    model.save(OUTPUT_DIR / "activity_model.keras")
    model.export(OUTPUT_DIR / "saved_model", format='tf_saved_model')

    # ── Detailed evaluation ──────────────────────────────────────────
    print("\n=== Detailed Evaluation ===")
    y_pred = np.argmax(model.predict(x_test, verbose=0), axis=1)
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=CLASS_NAMES))

    # ── Convert to int8-quantized TFLite ─────────────────────────────
    print("\nConverting to int8-quantized TFLite ...")

    # Stratified calibration set (from test set, as in tiny benchmark)
    x_cal = make_stratified_calibration(x_test, y_test, n_samples=200)
    print(f"  calibration set size: {len(x_cal)} (stratified)")

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = make_representative_dataset(x_cal)
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS_INT8,
    ]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8

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

    # ── Save test data for Axon compiler ──────────────────────────────
    test_data_path = OUTPUT_DIR / "test_data.npy"
    test_labels_path = OUTPUT_DIR / "test_labels.npy"
    np.save(test_data_path, x_test)
    np.save(test_labels_path, y_test)
    print(f"  saved test data  -> {test_data_path}  shape={x_test.shape}")
    print(f"  saved test labels -> {test_labels_path}  shape={y_test.shape}")

    # ── Save metadata for Axon compiler ──────────────────────────────
    meta_path = OUTPUT_DIR / "activity_model_meta.txt"
    with open(meta_path, "w") as f:
        f.write(f"model_name: ACTIVITY_MODEL\n")
        f.write(f"dataset: Capture24\n")
        f.write(f"annotation_scheme: {ANNOTATION_SCHEME}\n")
        f.write(f"window_size: {WINDOW_SIZE}\n")
        f.write(f"num_axes: {NUM_AXES}\n")
        f.write(f"num_classes: {NUM_CLASSES}\n")
        f.write(f"classes: {','.join(CLASS_NAMES)}\n")
        f.write(f"sample_rate_hz: {SAMPLE_RATE_HZ}\n")
        f.write(f"imu_position: wrist\n")
        f.write(f"accel_scale: plusminus_8g\n")
        f.write(f"input_scale_factor: {input_scale}\n")
        f.write(f"input_quant_scale: {q_scale_in}\n")
        f.write(f"input_quant_zp: {q_zp_in}\n")
        f.write(f"output_quant_scale: {q_scale_out}\n")
        f.write(f"output_quant_zp: {q_zp_out}\n")

    print(f"\n  saved -> {meta_path}")
    print("Done.")


if __name__ == "__main__":
    main()
