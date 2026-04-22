#
# Copyright (c) 2026 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: LicenseRef-Nordic-5-Clause
#

import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Activity Detection Model — Training Notebook

    10-class human activity recognition using the **Capture24** dataset
    (100 Hz triaxial accelerometer, wrist-worn Axivity AX3, ±8g).

    **Workflow:** Configure → Load Data → Explore → Train → Evaluate → Export
    """)
    return


@app.cell
def _():
    import os
    import time
    import glob
    import hashlib
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import tensorflow as tf
    from pathlib import Path
    import marimo as mo

    SEED = 42
    tf.random.set_seed(SEED)
    np.random.seed(SEED)

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
    NUM_CLASSES = len(CLASS_NAMES)
    NUM_AXES = 3
    return (
        CLASS_NAMES,
        NUM_AXES,
        NUM_CLASSES,
        Path,
        glob,
        hashlib,
        mo,
        np,
        os,
        pd,
        plt,
        tf,
        time,
    )


@app.cell
def _(mo):
    mo.md(r"""
    ## 1. Configuration
    """)
    return


@app.cell
def _(mo):
    window_size = mo.ui.number(start=25, stop=400, value=100, step=25,
                               label="Window size (samples)")
    stride = mo.ui.number(start=10, stop=200, value=25, step=5,
                          label="Stride (samples)")
    max_subjects = mo.ui.number(start=1, stop=151, value=60, step=1,
                                label="Max subjects (None = all)")
    batch_size = mo.ui.number(start=32, stop=512, value=128, step=32,
                              label="Batch size")
    learning_rate = mo.ui.number(start=1e-5, stop=0.01, value=0.001,
                                 step=1e-4, label="Learning rate")
    epochs = mo.ui.number(start=5, stop=200, value=20, step=5,
                          label="Max epochs")
    noise_stddev = mo.ui.number(start=0.0, stop=0.2, value=0.02,
                                step=0.01, label="Gaussian noise (augmentation)")
    dense_0 = mo.ui.number(start=32, stop=512, value=128, step=32,
                           label="Dense layer 0 units")
    dense_1 = mo.ui.number(start=16, stop=256, value=64, step=16,
                           label="Dense layer 1 units")

    mo.accordion({"Model & Training Parameters": mo.vstack([
        window_size, stride, max_subjects,
        batch_size, learning_rate, epochs, noise_stddev,
        dense_0, dense_1,
    ])})
    return (
        batch_size,
        dense_0,
        dense_1,
        epochs,
        learning_rate,
        max_subjects,
        noise_stddev,
        stride,
        window_size,
    )


@app.cell
def _(window_size):
    NUM_FEATURES = window_size.value * 3
    SAMPLE_RATE_HZ = 100
    return NUM_FEATURES, SAMPLE_RATE_HZ


@app.cell
def _(mo):
    mo.md(r"""
    ## 2. Load & Preprocess Data
    """)
    return


@app.cell
def _(CLASS_NAMES, NUM_AXES, Path, glob, hashlib, mo, np, os, pd):
    DATA_DIR = Path("data/capture24")
    CACHE_DIR = Path("cache/")
    ANNOTATION_SCHEME = "label:WillettsSpecific2018"


    def load_annotation_label_map(dict_path, scheme):
        df = pd.read_csv(dict_path)
        label_to_idx = {name: i for i, name in enumerate(CLASS_NAMES)}
        df["class_idx"] = df[scheme].map(label_to_idx)
        df = df.dropna(subset=["class_idx"])
        return dict(zip(df["annotation"], df["class_idx"].astype(int)))


    def extract_windows(accel, class_ids, window_size_, stride_):
        changes = np.where(class_ids[:-1] != class_ids[1:])[0] + 1
        segments = np.split(np.arange(len(class_ids)), changes)
        windows, labels = [], []
        for seg_indices in segments:
            if len(seg_indices) < window_size_:
                continue
            label = class_ids[seg_indices[0]]
            seg_accel = accel[seg_indices]
            start = 0
            while start + window_size_ <= len(seg_accel):
                windows.append(seg_accel[start:start + window_size_].flatten())
                labels.append(label)
                start += stride_
        if not windows:
            return (np.empty((0, window_size_ * NUM_AXES), dtype=np.float32),
                    np.empty(0, dtype=np.int64))
        return np.array(windows, dtype=np.float32), np.array(labels, dtype=np.int64)


    def _cache_key(ws, st, ms):
        payload = f"{ws}_{NUM_AXES}_{ANNOTATION_SCHEME}_{ms}_balanced"
        return hashlib.sha256(payload.encode()).hexdigest()[:12]


    def preprocess_dataset(window_size_, stride_, max_subjects_):
        cache = CACHE_DIR / f"windows_{_cache_key(window_size_, stride_, max_subjects_)}.npz"
        os.makedirs(CACHE_DIR, exist_ok=True)

        if cache.exists():
            data = np.load(cache)
            return data["x_windows"], data["y_labels"], True

        dict_path = DATA_DIR / "annotation-label-dictionary.csv"
        ann_to_class = load_annotation_label_map(dict_path, ANNOTATION_SCHEME)

        x_list, y_list = [], []
        subject_files = sorted(glob.glob(str(DATA_DIR / "P*.csv.gz")))
        if not subject_files:
            raise FileNotFoundError(f"No P*.csv.gz files found in {DATA_DIR}")

        max_s = max_subjects_ if max_subjects_ > 0 else None
        if max_s is not None:
            subject_files = subject_files[:max_s]

        for file in subject_files:
            name = Path(file).name
            print(f"  {name} ...", end="")
            df = pd.read_csv(file)[["x", "y", "z", "annotation"]]
            class_ids = df["annotation"].map(ann_to_class)
            valid = class_ids.notna()
            if valid.sum() == 0:
                print(" skip")
                continue
            accel = df.loc[valid, ["x", "y", "z"]].values.astype(np.float32)
            ids = class_ids[valid].values.astype(np.int64)
            w, l = extract_windows(accel, ids, window_size_, stride_)
            if len(l) > 0:
                x_list.append(w)
                y_list.append(l)
                print(f" {len(l)} windows")
            else:
                print(" no windows")

        if not x_list:
            raise RuntimeError("No windows extracted from any subject.")

        x_all = np.concatenate(x_list)
        y_all = np.concatenate(y_list)

        print(f"\n  Before balancing: {len(y_all):,} windows")
        from imblearn.under_sampling import RandomUnderSampler
        rus = RandomUnderSampler(random_state=42)
        x_all, y_all = rus.fit_resample(x_all, y_all)
        print(f"  After balancing:  {len(y_all):,} windows")

        np.savez_compressed(cache, x_windows=x_all, y_labels=y_all)
        size_mb = (x_all.nbytes + y_all.nbytes) / 1e6
        print(f"\n  Cached -> {cache} ({size_mb:.1f} MB)")
        return x_all, y_all, False

    load_button = mo.ui.run_button(label="Load / Refresh Data")
    load_button
    return ANNOTATION_SCHEME, load_button, preprocess_dataset


@app.cell
def _(
    SAMPLE_RATE_HZ,
    load_button,
    max_subjects,
    mo,
    preprocess_dataset,
    stride,
    window_size,
):
    mo.stop(not load_button.value, "Press **Load / Refresh Data** to continue.")

    ws = int(window_size.value)
    st = int(stride.value)
    ms = int(max_subjects.value)
    nf = ws * 3

    x_all_raw, y_all, from_cache = preprocess_dataset(ws, st, ms)

    status = "from cache" if from_cache else "from raw CSVs"
    mo.md(f"""
    **Loaded** {status}:
    - **Windows:** {len(y_all):,}
    - **Shape:** `{x_all_raw.shape}`
    - **Window:** {ws} samples ({ws / SAMPLE_RATE_HZ:.2f}s @ {SAMPLE_RATE_HZ}Hz)
    - **Features:** {nf}
    """)
    return x_all_raw, y_all


@app.cell
def _(mo):
    mo.md(r"""
    ## 3. Explore Data
    """)
    return


@app.cell
def _(CLASS_NAMES, np, plt, y_all):
    _unique, _counts = np.unique(y_all, return_counts=True)

    fig_dist, ax_dist = plt.subplots(figsize=(10, 4))
    colors = plt.cm.Set3(np.linspace(0, 1, len(CLASS_NAMES)))
    bars = ax_dist.bar(
        [CLASS_NAMES[int(i)] for i in _unique],
        _counts, color=colors[:len(_unique)]
    )
    ax_dist.set_ylabel("Window count")
    ax_dist.set_title("Class Distribution")
    ax_dist.tick_params(axis='x', rotation=45, labelsize=8)
    for bar, cnt in zip(bars, _counts):
        ax_dist.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                     f'{cnt:,}', ha='center', va='bottom', fontsize=7)
    plt.tight_layout()
    fig_dist
    return


@app.cell
def _(mo, y_all):
    sample_slider = mo.ui.slider(start=0, stop=min(200, len(y_all) - 1),
                                  value=0, label="Sample index")
    sample_slider
    return (sample_slider,)


@app.cell
def _(
    CLASS_NAMES,
    NUM_AXES,
    SAMPLE_RATE_HZ,
    np,
    plt,
    sample_slider,
    x_all_raw,
    y_all,
):
    _idx = int(sample_slider.value)
    _window = x_all_raw[_idx].reshape(-1, NUM_AXES)
    _label = CLASS_NAMES[int(y_all[_idx])]
    _t = np.arange(len(_window)) / SAMPLE_RATE_HZ

    fig_wave, axes_wave = plt.subplots(3, 1, figsize=(10, 5), sharex=True)
    axis_labels = ["X", "Y", "Z"]
    for i, ax in enumerate(axes_wave):
        ax.plot(_t, _window[:, i], linewidth=0.5)
        ax.set_ylabel(f"{axis_labels[i]} (m/s²)")
        ax.grid(True, alpha=0.3)
    axes_wave[-1].set_xlabel("Time (s)")
    axes_wave[0].set_title(f"Sample {_idx} — {_label}")
    plt.tight_layout()
    fig_wave
    return (i,)


@app.cell
def _(NUM_AXES, i, plt, x_all_raw):
    fig_hist, axes_hist = plt.subplots(1, 3, figsize=(12, 3))
    axis_names = ["X", "Y", "Z"]
    for k in range(3):
        vals = x_all_raw.reshape(-1, NUM_AXES)[:, k]
        axes_hist[k].hist(vals, bins=80, density=True, alpha=0.7)
        axes_hist[k].set_title(f"{axis_names[i]}-axis distribution")
        axes_hist[k].set_xlabel("m/s²")
        axes_hist[k].set_ylabel("Density")
        axes_hist[k].axvline(vals.mean(), color='red', linestyle='--',
                             label=f'μ={vals.mean():.2f}')
        axes_hist[k].legend(fontsize=7)
    plt.tight_layout()
    fig_hist
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 4. Normalize & Split
    """)
    return


@app.cell
def _(np):
    class PerAxisNormalizer:
        def __init__(self, num_axes):
            self.num_axes = num_axes
            self.means = None
            self.stds = None

        def fit(self, data):
            reshaped = data.reshape(-1, self.num_axes)
            self.means = reshaped.mean(axis=0)
            self.stds = reshaped.std(axis=0)
            self.stds = np.maximum(self.stds, 1e-6)
            return self

        def transform(self, data):
            reshaped = data.reshape(-1, self.num_axes)
            normalized = (reshaped - self.means) / self.stds
            return normalized.reshape(data.shape).astype(np.float32)

    return (PerAxisNormalizer,)


@app.cell
def _(mo):
    mo.md(r"""
    Per-axis z-score normalization (fit on train split only).
    """)
    return


@app.cell
def _(NUM_AXES, PerAxisNormalizer, np, x_all_raw, y_all):
    indices = np.arange(len(y_all))
    np.random.shuffle(indices)
    x_shuffled = x_all_raw[indices]
    y_shuffled = y_all[indices]

    split = int(0.8 * len(y_shuffled))
    x_train_raw, y_train = x_shuffled[:split], y_shuffled[:split]
    x_test_raw, y_test = x_shuffled[split:], y_shuffled[split:]

    normalizer = PerAxisNormalizer(NUM_AXES)
    normalizer.fit(x_train_raw)

    x_train = normalizer.transform(x_train_raw)
    x_test = normalizer.transform(x_test_raw)

    val_frac = 0.1
    val_count = int(val_frac * len(y_train))
    x_val, y_val = x_train[:val_count], y_train[:val_count]
    x_tr, y_tr = x_train[val_count:], y_train[val_count:]
    return normalizer, x_test, x_tr, x_val, y_test, y_tr, y_val


@app.cell
def _(mo, normalizer, x_test, x_tr, x_val):
    mo.md(f"""
    **Splits:**
    - Train: {x_tr.shape[0]:,} samples
    - Val: {x_val.shape[0]:,} samples
    - Test: {x_test.shape[0]:,} samples

    **Per-axis means:** `{normalizer.means}`
    **Per-axis stds:** `{normalizer.stds}`

    **Train range:** [{x_tr.min():.3f}, {x_tr.max():.3f}]
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 5. Train Model
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    Dense-only model compatible with Axon NPU (FullyConnected + ReLU).
    """)
    return


@app.cell
def _(
    NUM_CLASSES,
    NUM_FEATURES,
    batch_size,
    dense_0,
    dense_1,
    learning_rate,
    noise_stddev,
    np,
    tf,
):
    class ActivityDataset(tf.keras.utils.PyDataset):
        def __init__(self, x, y, batch_size_=128, shuffle=True, noise_stddev_=0.0):
            super().__init__()
            self.x = x
            self.y = y
            self.batch_size_ = batch_size_
            self.shuffle = shuffle
            self.noise_stddev_ = noise_stddev_
            self.indices = np.arange(len(self.y))
            if self.shuffle:
                np.random.shuffle(self.indices)

        def __len__(self):
            return int(np.ceil(len(self.y) / self.batch_size_))

        def __getitem__(self, idx):
            start = idx * self.batch_size_
            batch_idx = self.indices[start:start + self.batch_size_]
            x_batch = self.x[batch_idx].copy()
            y_batch = self.y[batch_idx]
            if self.noise_stddev_ > 0:
                x_batch += np.random.normal(0, self.noise_stddev_,
                                            x_batch.shape).astype(np.float32)
            return x_batch, y_batch

        def on_epoch_end(self):
            if self.shuffle:
                np.random.shuffle(self.indices)

    ff = int(NUM_FEATURES)
    d0 = int(dense_0.value)
    d1 = int(dense_1.value)
    bs = int(batch_size.value)
    ns = float(noise_stddev.value)

    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(ff,)),
        tf.keras.layers.Dense(d0, activation='relu', name='dense_0'),
        tf.keras.layers.Dense(d1, activation='relu', name='dense_1'),
        tf.keras.layers.Dense(NUM_CLASSES, activation='linear', name='output'),
    ], name="activity_detection")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=float(learning_rate.value)),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )

    model.summary()
    return ActivityDataset, bs, model, ns


@app.cell
def _(mo):
    train_button = mo.ui.run_button(label="Start Training")
    train_button
    return (train_button,)


@app.cell
def _(
    ActivityDataset,
    bs,
    epochs,
    mo,
    model,
    ns,
    tf,
    time,
    train_button,
    x_tr,
    x_val,
    y_tr,
    y_val,
):
    mo.stop(not train_button.value, "Press **Start Training** to begin.")

    train_ds = ActivityDataset(x_tr, y_tr, batch_size_=bs,
                               shuffle=True, noise_stddev_=ns)
    val_ds = ActivityDataset(x_val, y_val, batch_size_=bs, shuffle=False)

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_accuracy', patience=8,
            restore_best_weights=True, min_delta=0.001, mode='max'),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss', factor=0.5, patience=3,
            min_lr=1e-6, verbose=1),
    ]

    t0 = time.time()
    history = model.fit(train_ds, validation_data=val_ds,
                        epochs=int(epochs.value),
                        callbacks=callbacks, verbose=1)
    duration = time.time() - t0

    mo.md(f"**Training complete** in {duration:.1f}s ({duration / 60:.1f}min)")
    return (history,)


@app.cell
def _(history, plt):
    fig_train, (ax_loss, ax_acc) = plt.subplots(1, 2, figsize=(12, 4))

    ax_loss.plot(history.history['loss'], label='train')
    ax_loss.plot(history.history['val_loss'], label='val')
    ax_loss.set_title('Loss')
    ax_loss.set_xlabel('Epoch')
    ax_loss.legend()
    ax_loss.grid(True, alpha=0.3)

    ax_acc.plot(history.history['accuracy'], label='train')
    ax_acc.plot(history.history['val_accuracy'], label='val')
    ax_acc.set_title('Accuracy')
    ax_acc.set_xlabel('Epoch')
    ax_acc.legend()
    ax_acc.grid(True, alpha=0.3)

    plt.tight_layout()
    fig_train
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## 6. Evaluate
    """)
    return


@app.cell
def _(CLASS_NAMES, NUM_CLASSES, model, np, plt, x_test, y_test):
    loss, acc = model.evaluate(x_test, y_test, verbose=0)

    preds = np.argmax(model.predict(x_test, verbose=0), axis=1)
    per_class_correct = np.zeros(NUM_CLASSES, dtype=int)
    per_class_total = np.zeros(NUM_CLASSES, dtype=int)
    for i in range(len(y_test)):
        actual = int(y_test[i])
        per_class_total[actual] += 1
        if preds[i] == actual:
            per_class_correct[actual] += 1

    fig_eval, ax_eval = plt.subplots(figsize=(10, 4))
    class_accs = []
    class_labels = []
    for cls_id in range(NUM_CLASSES):
        if per_class_total[cls_id] > 0:
            ca = per_class_correct[cls_id] / per_class_total[cls_id]
            class_accs.append(ca)
            class_labels.append(CLASS_NAMES[cls_id])
    ax_eval.bar(class_labels, class_accs)
    ax_eval.set_ylabel("Accuracy")
    ax_eval.set_title(f"Per-Class Accuracy (overall: {acc:.4f}, loss: {loss:.4f})")
    ax_eval.tick_params(axis='x', rotation=45, labelsize=8)
    ax_eval.set_ylim(0, 1)
    for i, v in enumerate(class_accs):
        ax_eval.text(i, v + 0.01, f'{v:.2f}', ha='center', fontsize=7)
    plt.tight_layout()
    fig_eval
    return i, preds


@app.cell
def _(CLASS_NAMES, NUM_CLASSES, np, plt, preds, y_test):
    cm = np.zeros((NUM_CLASSES, NUM_CLASSES), dtype=int)
    for a, p in zip(y_test, preds):
        cm[int(a), int(p)] += 1

    fig_cm, ax_cm = plt.subplots(figsize=(10, 8))
    im = ax_cm.imshow(cm, cmap='Blues')
    ax_cm.set_xticks(range(NUM_CLASSES))
    ax_cm.set_yticks(range(NUM_CLASSES))
    ax_cm.set_xticklabels(CLASS_NAMES, rotation=45, ha='right', fontsize=7)
    ax_cm.set_yticklabels(CLASS_NAMES, fontsize=7)
    ax_cm.set_xlabel("Predicted")
    ax_cm.set_ylabel("Actual")
    ax_cm.set_title("Confusion Matrix")
    for i in range(NUM_CLASSES):
        for j in range(NUM_CLASSES):
            ax_cm.text(j, i, str(cm[i, j]),
                       ha='center', va='center',
                       color='white' if cm[i, j] > cm.max() / 2 else 'black',
                       fontsize=6)
    plt.colorbar(im, ax=ax_cm)
    plt.tight_layout()
    fig_cm
    return (i,)


@app.cell
def _(mo):
    mo.md(r"""
    ## 7. Export (TFLite int8)
    """)
    return


@app.cell
def _(mo):
    export_button = mo.ui.run_button(label="Export TFLite + Test Data")
    export_button
    return (export_button,)


@app.cell
def _(
    ANNOTATION_SCHEME,
    CLASS_NAMES,
    NUM_AXES,
    NUM_CLASSES,
    NUM_FEATURES,
    Path,
    SAMPLE_RATE_HZ,
    export_button,
    mo,
    model,
    normalizer,
    np,
    os,
    tf,
    x_test,
    y_test,
):
    mo.stop(not export_button.value, "Press **Export TFLite + Test Data** to continue.")

    OUTPUT_DIR = Path("output/")
    os.makedirs(str(OUTPUT_DIR), exist_ok=True)

    model.save(str(OUTPUT_DIR / "activity_model.keras"))
    model.export(str(OUTPUT_DIR / "saved_model"), format='tf_saved_model')

    def make_representative_dataset(calibration_data):
        def rep_dataset():
            for i in range(len(calibration_data)):
                yield [calibration_data[i:i + 1]]
        return rep_dataset

    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = make_representative_dataset(x_test[:500])
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8

    tflite_model = converter.convert()
    tflite_path = OUTPUT_DIR / "activity_model.tflite"
    tflite_path.write_bytes(tflite_model)

    np.save(str(OUTPUT_DIR / "test_data.npy"), x_test)
    np.save(str(OUTPUT_DIR / "test_labels.npy"), y_test)

    interp = tf.lite.Interpreter(model_path=str(tflite_path))
    interp.allocate_tensors()
    inp_det = interp.get_input_details()[0]
    out_det = interp.get_output_details()[0]
    q_scale_in = inp_det["quantization_parameters"]["scales"][0]
    q_zp_in = inp_det["quantization_parameters"]["zero_points"][0]
    q_scale_out = out_det["quantization_parameters"]["scales"][0]
    q_zp_out = out_det["quantization_parameters"]["zero_points"][0]

    correct_q = 0
    n_verify = min(1000, len(x_test))
    for i in range(n_verify):
        q_input = np.round(x_test[i:i + 1] / q_scale_in + q_zp_in).astype(np.int8)
        interp.set_tensor(inp_det["index"], q_input)
        interp.invoke()
        q_output = interp.get_tensor(out_det["index"])
        if np.argmax(q_output.flatten()) == y_test[i]:
            correct_q += 1
    quant_acc = correct_q / n_verify

    meta_path = OUTPUT_DIR / "activity_model_meta.txt"
    with open(str(meta_path), "w") as f:
        f.write(f"model_name: ACTIVITY_MODEL\n")
        f.write(f"dataset: Capture24\n")
        f.write(f"annotation_scheme: {ANNOTATION_SCHEME}\n")
        f.write(f"window_size: {int(NUM_FEATURES) // NUM_AXES}\n")
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

    mo.md(f"""
    **Export complete!**

    | Output | Size |
    |--------|------|
    | `activity_model.tflite` | {len(tflite_model):,} bytes |
    | `activity_model.keras` | saved |
    | `test_data.npy` | {x_test.shape} |
    | `test_labels.npy` | {y_test.shape} |
    | `activity_model_meta.txt` | saved |

    **Quantized accuracy:** {quant_acc:.4f} ({n_verify} samples)

    **Quantization params:** input scale={q_scale_in:.6f}, zp={q_zp_in}
    """)
    return (i,)


if __name__ == "__main__":
    app.run()
