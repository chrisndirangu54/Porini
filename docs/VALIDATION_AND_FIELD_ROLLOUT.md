# Scientific and operational acceptance gates

## Satellite
`pipelines/satellite_change.py` performs actual co-registered NDVI differencing on user-supplied band-aligned GeoTIFFs. Verify seasonal comparability, calibrated reflectance, optical cloud and shadow masks, terrain effects, raster alignment, GPS accuracy and ground truth. Radar requires a separate speckle/terrain correction model. No remote imagery is bundled.

## Gunshot and wildlife species recognition
`pipelines/model_inference.py` runs real ONNX models **only when supplied approved weights and a validation manifest**. `pipelines/validation.py` quantifies precision, recall, false positives and false negatives on labeled samples. Neither model weights nor independent field-validation datasets are in the repository. Never call a classifier scientifically validated without field trials and documented operating thresholds.

## Physical drone integration
`drone/telemetry.py` connects to a MAVLink endpoint and receives live read-only telemetry, but deliberately never transmits commands. No permitted autonomous takeoff or wildlife close approach is implemented; full physical control requires flight-test documentation, permissions, geofence enforcement and a certified pilot.

## Production identity
`PORINI_AUTH_MODE=oidc` enables OIDC JWT verification with issuer, audience, JWKS and tenant-scoped roles. Configure a trusted identity provider. Existing static keys are retained for development compatibility and **must never be exposed publicly**. Production also needs identity lifecycle, device certificate issuance, anomaly auditing, MFA and security penetration tests.

## Persistence
PostGIS schema and insert adapter support durable geospatial observations. The original SQLite event store remains the operational source until a transactional full data migration is completed. Do not mistake PostGIS support for a finished incident migration.

## Offline field clients
Flutter SQLCipher storage and outbox sync service are implemented, but full offline basemaps, SOS dispatch, cross-device conflict resolution and key lifecycle integration remain unfinished. Never depend on this prototype alone in remote emergencies.
