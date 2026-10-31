# Porini Sentinel: hardware and field validation protocol

This branch adds an optional one-frame RTSP/thermal reader, a local WAV reader, and an AES-256-GCM encrypted-file prototype. No real devices, models, or field sites have been connected. No trained or independently validated weights are supplied.

## Device pilots
- Optical and compatible thermal video can be sampled from provisioned RTSP endpoints with optional OpenCV; radiometric temperature requires manufacturer-specific calibration/SDK.
- WAV adapter reads locally collected, authorized acoustic sample files; production ALSA/USB capture, microphone calibration, environmental noise assessment, and continuous streaming are not implemented.
- Signed observation metadata can be posted through the existing secure edge endpoint. Keep device credentials out of code and logs.

## Evidence storage
AES-GCM helper encrypts bytes at rest with caller-provided 32-byte random key and restrictive local permissions, and returns a SHA-256 digest. The existing evidence manifest API does **not** yet call this helper, and this is not a remote encrypted vault. For production, integrate authenticated uploads, server-side integrity verification, per-tenant policies, key rotation, quotas, retention, KMS, protected backups, audit trails and secure retrieval.

## Independently verified AI / geographic evaluation
Collect consented sensor data with independently adjudicated labels. Freeze model weights and thresholds, partition sites geographically with buffer zones, and evaluate on weather/night/noise and habitat shifts. Report per-site precision/recall, calibration, false alarms per tower-day, detection delays, availability, energy use and environmental impact. Do not fabricate datasets, benchmarks or deployed outcomes.

## Pilot gates
1. Written permissions from conservancy, landowner and competent regulators where applicable.
2. Device-level network security, TLS, enrolled identities and tested revocation.
3. Privacy protections, restricted wildlife coordinates and retention limits.
4. Pre-declared benchmark metrics and independent ranger/fire-service reviewers.
5. Dry runs, documented incident handling and rollback; prohibit autonomous enforcement, targeting or suppressant deployment.
