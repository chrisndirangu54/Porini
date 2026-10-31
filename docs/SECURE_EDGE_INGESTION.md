# Porini Sentinel secure sensor ingestion

## Implemented
Per-device HMAC-signed observation intake:
`POST /towers/{tower_id}/signed-observations`.

After an administrator registers a tower and sensor, provision a unique random 32+ character secret in `PORINI_SENSOR_HMAC_KEYS` as a JSON map keyed by sensor UUID. Never commit keys or include them in sensor messages. Provision keys through a secrets manager in deployed installations. The sender signs the exact raw JSON bytes with HMAC-SHA256 using `timestamp + "\\n" + body` and submits headers `X-Sensor-ID`, `X-Device-Timestamp`, `X-Device-Signature`. Server checks a two-minute clock skew window, registered sensor-to-tower ownership, signature, bounded body, and nonempty unique `external_id`. Use TLS termination on production ingestion. HMAC keys are only a transitional identity mechanism, not certificate-based device attestation.

`app.edge_adapter.publish(...)` offers an example standard-library HTTPS sender for **preclassified event metadata**. Event records pass into existing Porini incident intake with explicit confidence and human review. Authentication of ordinary `/towers/{id}/observations` remains role-key based: disable shared sensor API keys and lock down legacy routes at the gateway before production.

## Real camera/thermal/acoustic rollout — not yet connected
1. Optical/infrared RTSP/ONVIF, radiometric thermal drivers, and microphone ALSA/USB capture should run as isolated edge processes, ideally with manufacturer-supported SDKs.
2. Normalize timestamps, calibration, coordinates and lens/sensor capability metadata. Use secure local encrypted buffers for short clips.
3. On-device models should produce candidate detections, quality indicators and evidence hashes, **never presumed confirmation of criminal conduct**.
4. Ship only metadata on the signed endpoint; evidence needs separate authenticated encrypted object storage and retention policy.
5. Record model weights/version, calibration dataset, confusion matrix, precision/recall, false alarms per sensor-day, OOD detection, site-held-out tests and ranger-reviewed field outcomes.
6. Conduct controlled field trials with consent and applicable wildlife/privacy permits. Include degraded connectivity, battery, wind noise, smoke haze, rain, nighttime and false positive scenarios.
7. Migrate SQLite to PostgreSQL/PostGIS, move device secrets to a vault, use mTLS/device certificates and audited revocation/rotation before critical deployment.

**Safety:** No automated drone launching, targeting, interception, suppression discharge or adverse action against a person. Human-approved ranger and fire-authority workflows only.
