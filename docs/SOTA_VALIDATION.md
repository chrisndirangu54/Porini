# Porini: model evidence and SOTA evaluation

This upgrade establishes a research-grade **evaluation foundation**, not live pretrained-model inference.

## Candidate adapters (not installed)
- **MegaDetector V6**: camera-trap object detection (animal/person/vehicle). Does not identify species or criminal intent. Choose license-compatible model variant and validate locally.
- **Google SpeciesNet**: downstream species identification in camera-trap photographs. Confirm species coverage and accuracy on local habitats.
- **NASA FIRMS VIIRS**: candidate active-fire detections with acquisition age, uncertainty and sensor metadata; not a live fire boundary.

## Required before production
1. Geographic and temporal holdouts by park, site/camera, season and sensor model; prevent repeated individuals or near-duplicate frames crossing splits.
2. Report precision, recall, false alerts per camera-day, macro F1, class-wise recall, Brier score, calibration plots, latency and confidence intervals; track environmental domain shift.
3. Record consent, permitted use, dataset and model licenses, model lineage, human ground truth and independent review.
4. Sensitivity-based access to threatened-species locations and identifiable human detections; do not infer poaching from mere human presence.
5. Offline-first ranger interfaces with resilient queueing; PostGIS, event delivery and encrypted evidence store must be separately verified.
6. Satellite observations and camera alerts require independent confirmation before any intervention.
7. Do not automatically trigger drone flight, chemical discharge, arrest or confrontation.

The Python `evidence_quality.py` module exposes validation, cohort metrics and conservative review flags, without network calls or inference. Real external integrations must be built and tested separately.
