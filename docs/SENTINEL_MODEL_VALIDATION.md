# Sentinel model validation protocol

**Status: evaluation tooling only, no field-validated classifiers.**

1. Define target and sampling unit in advance. Build licensed, consented, ranger-reviewed datasets for smoke, flame, chainsaw and gunshot candidate events; label uncertain samples separately rather than forcing negatives.
2. Split by **site**, not random frames. Keep whole towers, adjacent recording sessions and correlated geographic neighborhoods in the same split. Reserve independent geographic test locations prior to model selection.
3. Record daylight/night/twilight, weather, species habitat, microphone configuration, infrared calibration, smoke haze, sensor height and background noise.
4. Fit models and choose decision thresholds on train/validation sites. Use a frozen threshold on the independent test set. Evaluate precision, recall, specificity, F1, calibration, and per-site/per-weather subgroup errors. Report confidence intervals and subgroup sample counts.
5. For operational evaluation, measure **false alarms per sensor-day**, event detection delay, missed confirmed incidents, bandwidth, duty cycle, battery consumption, ranger workload and site-specific generalization.
6. Preserve evidence with cryptographic hashes, encryption at rest, restricted short retention and review logs. For potentially identifiable people, apply minimization and access controls; do not classify criminality based solely on sensor output.
7. Require qualified ranger / fire authority review, permissions, environmental assessments and documented emergency escalation. No automatic targeting or suppression discharge.

The pure-Python `app.model_validation.evaluate` function accepts verified precomputed model scores and human ground-truth labels. It rejects duplicate sample IDs, geographical site leakage, missing independent test data and mixed model versions; reports overall and stratified confusion-matrix metrics. It does **not** download datasets, train classifiers, operate cameras, or validate any real field model.

Future integration: approved ONVIF/RTSP thermal/optical devices, ALSA/USB acoustic input, weather telemetry, encrypted evidence vault, per-site calibration and independent external evaluation. Connectivity depends on real device specifications and credentials.
