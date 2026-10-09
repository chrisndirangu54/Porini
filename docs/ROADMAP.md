# Porini integrated conservation capability map

## Implemented in repository
- Event ingestion for acoustics, thermal/night vision, visible cameras, satellite metadata, drones, GPS collars, IoT and ranger reports
- Incident triage, cross-observation temporal/geospatial correlation, priorities and ranger assignment records
- Incident command dashboard, mapping, synthetic demo events, audited human approval workflow for observation requests
- SQLite-backed additional conservation record catalog with tenant scope, verification gate, GeoJSON and verified sighting summary
- Acoustic impulsiveness feature extractor (not species/gunshot classification)
- STAC imagery metadata validator (not remote sensing processing)
- MQTT payload adapter (not connected to a running broker)
- CI smoke tests and Docker API

## Next: high-priority production integrations
1. Replace legacy in-memory incident/event/mission data with PostgreSQL/PostGIS + Alembic migrations and durable messaging.
2. OIDC, hardware attestation, per-device/service identities, evidence store with integrity hashes and policies, fine-grained RBAC per conservation organization.
3. Physical field devices: LoRaWAN gateways, MQTT broker, acoustic sensor drivers, camera trap pipelines, solar/storage/battery health.
4. Trained species and acoustic classifiers: BirdNET, MegaDetector, OpenSoundscape, PyTorch/ONNX inference adapters with benchmark datasets.
5. Human-supervised UAV telemetry/video integration with PX4/MAVSDK, permits, geofences and wildlife disturbance protections.
6. Satellite science workers: pystac-client, Sentinel-1/2, Landsat, NASA FIRMS, rasterio/stackstac and verified alert pipelines.
7. Flutter offline-first ranger application with field GPS and secure communications.
8. Real notification channels (SMS, push, email, radio gateway), delivery receipts, escalation and out-of-band fallbacks.

## Advanced ecological modules (schema and roadmap, not validated models)
- Human–wildlife conflict and road crossing early warning
- Waterhole hydrology and possible contamination
- Animal activity and population estimation with sampling bias correction
- Individual wildlife re-identification with species-specific validation
- Veterinary / injury detection reviews; zoonotic disease reporting
- Habitat connectivity, restoration outcomes and invasive species mapping
- Biodiversity bioacoustic monitoring and seasonality analysis
- Wildfire / smoke / heat hazard monitoring
- Marine protected area hydroacoustics and vessel sightings where licensed
- Community sightings, scientific annotation, citizen science verification
- Ecology knowledge graph, simulation/digital twin, model registry, uncertainty-aware reporting
- Multi-conservancy incident cooperation with explicit sharing permissions
- Research dataset export, FAIR metadata, standardized ecology metrics, model-drift analysis
- Self-healing infrastructure, energy-aware inference and intermittent-network synchronisation

## Open ecosystems to evaluate
EarthRanger, SMART Conservation Software, Wildlife Insights, GBIF, iNaturalist, Movebank, BirdNET, OpenSoundscape, MegaDetector, PyTorch, ONNX Runtime, OpenCV, QGIS, PostGIS, GeoServer, STAC, GDAL, Copernicus, NASA FIRMS, OpenDroneMap, PX4, MAVSDK, ROS 2, ChirpStack, Mosquitto, LoRaWAN, Home Assistant where appropriately scoped, and Grafana/Prometheus.

Names above identify prospective interoperable technologies, **not** activated vendor accounts or completed integrations. Review terms, consent, privacy and scientific limitations independently.
