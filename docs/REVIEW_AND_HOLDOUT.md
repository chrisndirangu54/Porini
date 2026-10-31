# Research review and reproducible evaluation

- `backend/app/review_queue.py` provides a tenant-scoped, persistent human review queue for research candidates. It is not yet wired into an authenticated HTTP endpoint and must not be exposed without OIDC, strong tenant isolation and auditing.
- `scripts/evaluate_holdout.py` accepts real `group,label,score` CSV data and computes per-group and overall metrics, including the Brier score. Rows must be independent labeled observations with distinct site/time splits.
- Do not upload sensitive wildlife coordinates, ranger personal data or identifiable images to public repositories.
- The review queue is a development SQLite backend, not a production multi-tenant evidence vault.
- No trained weights, GPU infrastructure, species-calibration datasets, real sensor credentials or field deployments have been supplied. These steps cannot truthfully be marked complete.
