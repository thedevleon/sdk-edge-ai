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
import hashlib
import numpy as np
import pandas as pd
import tensorflow as tf
from pathlib import Path

SEED = 42
tf.random.set_seed(SEED)
np.random.seed(SEED)

# ── Model / data parameters ─────────────────────────────────────────
WINDOW_SIZE = 100         # samples per inference window (1.0 s @ 100 Hz)
NUM_AXES = 3              # accel x, y, z
NUM_FEATURES = WINDOW_SIZE * NUM_AXES
NUM_CLASSES = 10
SAMPLE_RATE_HZ = 100      # Capture24 IMU sample rate

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
OUTPUT_DIR = Path("output/")
CACHE_DIR = Path("cache/")

# Set to an int to limit the number of subjects loaded (None = all).
MAX_SUBJECTS = 60

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

    Returns (windows, labels) where each window is flattened
    (window_size * NUM_AXES,) float32.
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
            win = seg_accel[start:start + window_size].flatten()
            windows.append(win)
            labels.append(label)
            start += stride

    if not windows:
        return (np.empty((0, window_size * NUM_AXES), dtype=np.float32),
                np.empty(0, dtype=np.int64))

    return np.array(windows, dtype=np.float32), np.array(labels, dtype=np.int64)


def _cache_key() -> str:
    """Deterministic cache key from all parameters that affect windowing."""
    payload = f"{WINDOW_SIZE}_{NUM_AXES}_{ANNOTATION_SCHEME}_{MAX_SUBJECTS}"
    return hashlib.sha256(payload.encode()).hexdigest()[:12]


def _cache_path() -> Path:
    return CACHE_DIR / f"windows_{_cache_key()}.npz"


def preprocess_dataset(stride: int = 25):
    """Load all subjects, extract windows, and cache to disk as .npz.

    Skips the expensive CSV parsing + windowing if a matching cache exists.
    """
    cache = _cache_path()
    os.makedirs(CACHE_DIR, exist_ok=True)

    if cache.exists():
        print(f"\n  Found cached dataset: {cache}")
        data = np.load(cache)
        return data["x_windows"], data["y_labels"]

    print("\n  No cache found — preprocessing from raw CSVs ...")
    dict_path = DATA_DIR / "annotation-label-dictionary.csv"
    ann_to_class = load_annotation_label_map(dict_path, ANNOTATION_SCHEME)

    x_list, y_list = [], []

    subject_files = sorted(glob.glob(str(DATA_DIR / "P*.csv.gz")))

    if not subject_files:
        raise FileNotFoundError(f"No P*.csv.gz files found in {DATA_DIR}")

    if MAX_SUBJECTS is not None:
        subject_files = subject_files[:MAX_SUBJECTS]

    for file in subject_files:
        name = Path(file).name
        print(f"    {name} ...", end="")
        df = pd.read_csv(file)[["x", "y", "z", "annotation"]]

        class_ids = df["annotation"].map(ann_to_class)
        valid = class_ids.notna()

        if valid.sum() == 0:
            print(" no valid annotations, skipping")
            continue

        accel = df.loc[valid, ["x", "y", "z"]].values.astype(np.float32)
        ids = class_ids[valid].values.astype(np.int64)

        w, l = extract_windows(accel, ids, WINDOW_SIZE, stride)

        if len(l) > 0:
            x_list.append(w)
            y_list.append(l)
            print(f" {len(l)} windows")
        else:
            print(" no windows extracted")

    if not x_list:
        raise RuntimeError("No windows extracted from any subject.")

    x_all = np.concatenate(x_list)
    y_all = np.concatenate(y_list)

    np.savez_compressed(cache, x_windows=x_all, y_labels=y_all)
    size_mb = (x_all.nbytes + y_all.nbytes) / 1e6
    print(f"\n  Cached -> {cache}  ({size_mb:.1f} MB)")

    return x_all, y_all


# ── PyDataset ────────────────────────────────────────────────────────

class ActivityDataset(tf.keras.utils.PyDataset):
    """Keras PyDataset backed by an in-memory numpy array.

    Handles shuffling and optional on-the-fly Gaussian noise augmentation.
    """

    def __init__(self, x: np.ndarray, y: np.ndarray, batch_size: int = 128,
                 shuffle: bool = True, noise_stddev: float = 0.0, **kwargs):
        super().__init__(**kwargs)
        self.x = x
        self.y = y
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.noise_stddev = noise_stddev
        self.indices = np.arange(len(self.y))
        if self.shuffle:
            np.random.shuffle(self.indices)

    def __len__(self) -> int:
        return int(np.ceil(len(self.y) / self.batch_size))

    def __getitem__(self, idx: int):
        start = idx * self.batch_size
        batch_idx = self.indices[start:start + self.batch_size]

        x_batch = self.x[batch_idx].copy()
        y_batch = self.y[batch_idx]

        if self.noise_stddev > 0:
            x_batch += np.random.normal(0, self.noise_stddev,
                                        x_batch.shape).astype(np.float32)
        return x_batch, y_batch

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indices)


# ── Helpers ──────────────────────────────────────────────────────────

def make_representative_dataset(calibration_data: np.ndarray):
    """Return a callable yielding samples for TFLite int8 calibration."""
    def rep_dataset():
        for i in range(len(calibration_data)):
            yield [calibration_data[i:i + 1]]
    return rep_dataset


class PerAxisNormalizer:
    """Per-axis z-score normalization computed on training data."""

    def __init__(self):
        self.means = None
        self.stds = None

    def fit(self, data: np.ndarray):
        """Fit on (N, NUM_FEATURES) flattened data."""
        reshaped = data.reshape(-1, NUM_AXES)
        self.means = reshaped.mean(axis=0)
        self.stds = reshaped.std(axis=0)
        self.stds = np.maximum(self.stds, 1e-6)
        print(f"  Per-axis means: {self.means}")
        print(f"  Per-axis stds:  {self.stds}")
        return self

    def transform(self, data: np.ndarray) -> np.ndarray:
        reshaped = data.reshape(-1, NUM_AXES)
        normalized = (reshaped - self.means) / self.stds
        return normalized.reshape(data.shape).astype(np.float32)


# ── Keras model ──────────────────────────────────────────────────────

def build_model() -> tf.keras.Model:
    """Dense-only model compatible with Axon NPU (FullyConnected + ReLU)."""
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(NUM_FEATURES,)),
        tf.keras.layers.Dense(128, activation='relu', name='dense_0'),
        tf.keras.layers.Dense(64, activation='relu', name='dense_1'),
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

    # ── Preprocess (load from cache or build from raw CSVs) ──────────
    print("\nPreprocessing dataset ...")
    x_all, y_all = preprocess_dataset(stride=25)
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
    x_train_raw, y_train = x_all[:split], y_all[:split]
    x_test_raw, y_test = x_all[split:], y_all[split:]

    # ── Per-axis z-score normalization (fit on train only) ───────────
    print("\nFitting per-axis normalizer on training data ...")
    normalizer = PerAxisNormalizer()
    normalizer.fit(x_train_raw)

    x_train = normalizer.transform(x_train_raw)
    x_test = normalizer.transform(x_test_raw)

    print(f"\n  train: {x_train.shape}  test: {x_test.shape}")
    print(f"  train range: [{x_train.min():.3f}, {x_train.max():.3f}]")

    # ── Build PyDatasets ─────────────────────────────────────────────
    val_split = 0.1
    val_count = int(val_split * len(y_train))

    x_val = x_train[:val_count]
    y_val = y_train[:val_count]
    x_tr = x_train[val_count:]
    y_tr = y_train[val_count:]

    train_ds = ActivityDataset(x_tr, y_tr, batch_size=128,
                               shuffle=True, noise_stddev=0.02)
    val_ds = ActivityDataset(x_val, y_val, batch_size=128, shuffle=False)

    # ── Train float model ────────────────────────────────────────────
    model = build_model()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )
    model.summary()

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_accuracy', patience=8, restore_best_weights=True,
            min_delta=0.001, mode='max'),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=3,
            min_lr=1e-6, verbose=1),
    ]

    print("\nTraining ...")
    total_start = time.time()
    model.fit(train_ds, validation_data=val_ds, epochs=20,
              callbacks=callbacks, verbose=1)
    total_duration = time.time() - total_start
    print(f"\nTotal training time: {total_duration:.1f}s ({total_duration/60:.1f}min)")

    loss, acc = model.evaluate(x_test, y_test, verbose=0)
    print(f"\nFloat model - test accuracy: {acc:.4f}  loss: {loss:.4f}")

    # --- Save model ---
    model.save(OUTPUT_DIR / "activity_model.keras")
    model.export(OUTPUT_DIR / "saved_model", format='tf_saved_model')

    # ── Convert to int8-quantized TFLite ─────────────────────────────
    print("\nConverting to int8-quantized TFLite ...")

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = make_representative_dataset(x_test[:500])
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS_INT8,
    ]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8

    tflite_model = converter.convert()

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
    n_verify = min(1000, len(x_test))
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

    # ── Save normalization metadata ──────────────────────────────────
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
        f.write(f"normalization: per_axis_zscore\n")
        f.write(f"axis_means: {','.join(f'{v:.6f}' for v in normalizer.means)}\n")
        f.write(f"axis_stds: {','.join(f'{v:.6f}' for v in normalizer.stds)}\n")
        f.write(f"input_quant_scale: {q_scale_in}\n")
        f.write(f"input_quant_zp: {q_zp_in}\n")
        f.write(f"output_quant_scale: {q_scale_out}\n")
        f.write(f"output_quant_zp: {q_zp_out}\n")

    print(f"\n  saved -> {meta_path}")
    print("Done.")


if __name__ == "__main__":
    main()
