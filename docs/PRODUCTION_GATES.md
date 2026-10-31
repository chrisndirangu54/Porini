# Production readiness gates

**Not deployment ready.** No real ranger alert is automatically confirmed, no autonomous flights, release controls or enforcement.

1. PostGIS migration is defined but must be applied in managed DB with tenant isolation, RLS, backups, and performance load testing.
2. Evidence SHA-256 manifests are supported; encrypted storage, legal chain of custody and tamper-evident persistence are not yet implemented.
3. SpeciesNet adapter requires validated pinned SDK, model weights, licensing, GPU fallback and field ground truth before serving real observations. API compatibility must be tested against installed version.
4. BirdNET, MegaDetector, FIRMS, actual STAC raster download and change detection still require integration and real data.
5. Add offline ranger synchronization conflict tests and field trials.
6. Run CI, region-holdout accuracy evaluation, protected-species privacy review, security penetration tests and operations drills.
