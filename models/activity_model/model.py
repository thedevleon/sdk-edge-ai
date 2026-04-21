#
# Copyright (c) 2026 Nordic Semiconductor ASA
#
# SPDX-License-Identifier: LicenseRef-Nordic-5-Clause
#

"""
Activity Detection Model Definitions
=====================================

Model architectures adapted from MLCommons TinyML benchmark suite and
optimised for triaxial accelerometer activity classification.

All models share the same interface:
  - Input:  (WINDOW_SIZE, NUM_AXES) float32 — shape (50, 3)
  - Output: NUM_CLASSES logits (linear activation)

Select a model by setting SELECTED_MODEL to one of the MODEL_REGISTRY keys.
"""

import tensorflow as tf
from tensorflow.keras import layers, Model, regularizers

SELECTED_MODEL = "cnn"

MODEL_REGISTRY = {}


def register_model(name):
    def decorator(fn):
        MODEL_REGISTRY[name] = fn
        return fn
    return decorator


def build_model(model_name: str,
                window_size: int,
                num_axes: int,
                num_classes: int) -> tf.keras.Model:
    if model_name not in MODEL_REGISTRY:
        raise ValueError(
            f"Unknown model '{model_name}'. "
            f"Available: {list(MODEL_REGISTRY.keys())}"
        )
    return MODEL_REGISTRY[model_name](window_size, num_axes, num_classes)


# ── Dense models ──────────────────────────────────────────────────────


@register_model("dense")
def dense(window_size, num_axes, num_classes):
    """Two-hidden-layer dense network (original model)."""
    return tf.keras.Sequential([
        layers.Input(shape=(window_size, num_axes)),
        layers.Flatten(),
        layers.Dense(128, activation='relu', name='dense_0'),
        layers.Dense(64, activation='relu', name='dense_1'),
        layers.Dense(num_classes, activation='linear', name='output'),
    ], name="dense")


@register_model("fc4")
def fc4(window_size, num_axes, num_classes):
    """Four-layer FC with BatchNorm + Dropout (from KWS benchmark).

    Adapted from keyword_spotting/keras_model.py 'fc4' architecture.
    """
    return tf.keras.Sequential([
        layers.Input(shape=(window_size, num_axes)),
        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.2),
        layers.BatchNormalization(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.2),
        layers.BatchNormalization(),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.2),
        layers.BatchNormalization(),
        layers.Dense(num_classes, activation='linear', name='output'),
    ], name="fc4")


# ── 1-D Convolutional models ─────────────────────────────────────────


@register_model("cnn")
def cnn_1d(window_size, num_axes, num_classes):
    """Simple 1-D CNN for time-series activity recognition.

    Conv1D slides across the time axis; num_axes is the channel dimension.
    """
    return tf.keras.Sequential([
        layers.Input(shape=(window_size, num_axes)),
        layers.Conv1D(64, 5, strides=2, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.Conv1D(64, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.Conv1D(64, 3, padding='same', activation='relu'),
        layers.BatchNormalization(),
        layers.GlobalAveragePooling1D(),
        layers.Dropout(0.4),
        layers.Dense(num_classes, activation='linear', name='output'),
    ], name="cnn_1d")


@register_model("ds_cnn")
def ds_cnn_1d(window_size, num_axes, num_classes):
    """Depthwise-separable 1-D CNN (from KWS benchmark).

    Adapted from keyword_spotting/keras_model.py 'ds_cnn' architecture,
    converted from 2-D spectrogram operations to 1-D time-series.
    """
    weight_decay = 1e-4
    reg = regularizers.L2(weight_decay)

    inputs = layers.Input(shape=(window_size, num_axes))

    x = layers.Conv1D(64, 5, strides=2, padding='same',
                      kernel_regularizer=reg)(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)
    x = layers.Dropout(0.2)(x)

    for _ in range(4):
        x = layers.SeparableConv1D(64, 3, padding='same',
                                   depthwise_regularizer=reg,
                                   pointwise_regularizer=reg)(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)

    x = layers.Dropout(0.4)(x)
    x = layers.GlobalAveragePooling1D()(x)
    outputs = layers.Dense(num_classes, activation='linear',
                           name='output')(x)

    return Model(inputs=inputs, outputs=outputs, name="ds_cnn_1d")


@register_model("resnet")
def resnet_1d(window_size, num_axes, num_classes):
    """Small 1-D ResNet (from image classification benchmark).

    Adapted from image_classification/keras_model.py 'resnet_v1_eembc',
    converted from 2-D image convolutions to 1-D time-series.

    Three residual stacks with doubling filters at each stride-2 transition.
    """
    num_filters = 16
    reg = regularizers.L2(1e-4)

    inputs = layers.Input(shape=(window_size, num_axes))

    x = layers.Conv1D(num_filters, 3, strides=1, padding='same',
                      kernel_initializer='he_normal',
                      kernel_regularizer=reg)(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Activation('relu')(x)

    for stack_idx, stride in enumerate([1, 2, 2]):
        y = layers.Conv1D(num_filters, 3, strides=stride, padding='same',
                          kernel_initializer='he_normal',
                          kernel_regularizer=reg)(x)
        y = layers.BatchNormalization()(y)
        y = layers.Activation('relu')(y)
        y = layers.Conv1D(num_filters, 3, strides=1, padding='same',
                          kernel_initializer='he_normal',
                          kernel_regularizer=reg)(y)
        y = layers.BatchNormalization()(y)

        if stride != 1:
            x = layers.Conv1D(num_filters, 1, strides=stride, padding='same',
                              kernel_initializer='he_normal',
                              kernel_regularizer=reg)(x)

        x = layers.Add()([x, y])
        x = layers.Activation('relu')(x)

        num_filters *= 2

    x = layers.GlobalAveragePooling1D()(x)
    outputs = layers.Dense(num_classes, activation='linear',
                           kernel_initializer='he_normal',
                           name='output')(x)

    return Model(inputs=inputs, outputs=outputs, name="resnet_1d")
