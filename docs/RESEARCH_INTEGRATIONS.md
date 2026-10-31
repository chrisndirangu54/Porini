# Porini research integrations — implementation status

New authenticated API:
- `GET /research/models`: model candidates, dependency checks, no simulated detections.
- `POST /research/images/review`: validates a locally staged image in `PORINI_EVIDENCE_ROOT`, returns readiness; **does not yet execute model inference**.
- `POST /research/audio/review`: local audio-file validation and BirdNET readiness; no recognition model executed.
- `POST /research/stac/metadata`: extracts and validates satellite scene metadata, without asserting fire detection.

`backend/app/stac_pipeline.py` also provides optional allowlisted STAC querying when `pystac-client` is installed and credentials/configuration permit. It is not exposed as an arbitrary-URL API. `backend/app/evidence_quality.py` implements evidence provenance, fresh observation checks, Brier score, classification metrics and cohort reports. These statistics are **not measured real-world Porini model performance**.

## Remaining SOTA milestones
1. Install and pin properly licensed model weights for MegaDetector, SpeciesNet, and BirdNET; implement their documented SDK inference, batching and GPU/CPU fallback. Store model hashes, inference time and confidence calibration.
2. Configure credentialed STAC sources; read actual rasters, spatially align bands, cloud-mask and combine baseline imagery; ingest NASA FIRMS according to its data license and observation time.
3. Durable PostGIS spatial tables, migrations, organization isolation, retention rules, audit evidence chain and a message broker with dead-letter/retry policy.
4. Ranger mobile offline queue with tested conflict-resolution, verified offline maps and sync under intermittent connections.
5. Ecological ground-truth datasets across habitats and seasons, independent site holdouts, error analysis, precision/recall and calibration with confidence intervals.
6. Dashboard presentation of human-review evidence quality, not law-enforcement classifications or verified fire alerts from model-only data.
7. Real sensor field tests and human factors / wildlife disturbance review. No autonomous flight, suppression or enforcement activation.

This branch is a substantial integration scaffold, **not a finished state-of-the-art deployed system**.
