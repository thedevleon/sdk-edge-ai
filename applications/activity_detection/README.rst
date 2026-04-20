.. _app_activity_detection:

Activity Detection
##################

This application demonstrates human activity recognition using a
LIS2DUX12 triaxial accelerometer on the I2C bus and the Axon NPU
for neural network inference on the nRF54LM20DK.

Supported activities
********************

============  ================
Class index   Activity
============  ================
0             Sitting
1             Standing
2             Lying down
3             Walking
4             Running
5             Cycling
6             Workout
============  ================

The model is trained on the `PAMAP2`_ dataset at 100 Hz using the
hand/wrist IMU accelerometer (±16 g scale).

.. _PAMAP2: https://archive.ics.uci.edu/dataset/231/pamap2+physical+activity+monitoring

Hardware setup
**************

.. table::
   :align: center

   ==========  ========  ========
   Signal      nRF Pin   LIS2DUX12
   ==========  ========  ========
   SDA         P1.04     SDA/SDO
   SCL         P1.05     SCL
   VDD         VDD       VDD
   GND         GND       GND
   ==========  ========  ========

Build and run
*************

Prerequisites:

* nRF Connect SDK v3.3.0-preview2 (or compatible)
* The Axon-compiled model header at
  :file:`src/generated/nrf_axon_model_activity_detection.h`

Step 1 — Train the model (requires Docker with ROCm or TensorFlow):

.. code-block:: console

   cd models/activity_model
   ./run.sh train

Step 2 — Compile for Axon NPU (runs inside the same container):

.. code-block:: console

   ./run.sh compile

Step 3 — Build the Zephyr application:

.. code-block:: console

   west build -b nrf54lm20dk/nrf54lm20b/cpuapp applications/activity_detection
   west flash
