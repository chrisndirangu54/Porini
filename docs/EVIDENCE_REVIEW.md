# Sentinel evidence review — prototype

This component registers SHA-256 hashes and evidence metadata (incident, sensor, capture time, model version, length and MIME type), then stores human ranger reviews in SQLite. **It does not store, upload, encrypt, or authenticate raw media.** Hashes are supplied by clients and not independently verified against the media in the current prototype. Reviews are distinct from model predictions.

Endpoints:
- POST /evidence/manifests (admin/ranger)
- GET /evidence/incidents/{incident_id} (admin/ranger)
- POST /evidence/{manifest_id}/reviews (admin/ranger)
- GET /evidence/{manifest_id}/reviews (admin/ranger)

Production follow-up: authenticated direct upload to encrypted S3-compatible object storage, server-side hash verification, object-level access controls, tenant isolation, audit retention and deletion policies, malware checks, per-device provenance and OIDC identities. Restrict wildlife coordinates and identifiable human footage. Model benchmarking must use independently adjudicated ground truth, not a single unverified review.
