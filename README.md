# Porini — Wildlife Conservation Intelligence

An open, event-driven conservation monitoring starter for rangers, researchers, and conservancies. **Prototype, not a deployed emergency or anti-poaching service.** No live drones, satellite feeds, government dispatch services, or real sensors are connected by default. Demo observations are synthetic and clearly labeled.

## Included
- Python/FastAPI event ingestion and incident triage with evidence, confidence, severity and localization uncertainty.
- Acoustic classification event adapter; camera, drone, satellite, GPS collar, and IoT event schemas.
- Multi-observation temporal/geospatial correlation and review-first incident workflow.
- Ranger dispatch assignments and **human-approved** drone reconnaissance requests, with no flight-control hardware commands.
- React operations dashboard: incidents, severity, sensors, event ingestion, map, and mission approvals.
- Event audit trail, synthetic seed data, role-aware API-key authentication, unit tests, Docker and CI.
- Modular ingestion boundaries for future MQTT, Sentinel imagery, acoustic ML, PX4/MAVLink, and LoRaWAN adapters.

## Quick start
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
PORINI_API_KEY=local-dev-key uvicorn app.main:app --reload
```
In another terminal:
```bash
cd dashboard
npm install
npm run dev
```
Dashboard: http://localhost:5173; API docs: http://localhost:8000/docs. Dashboard demo key defaults to `local-dev-key`; replace before any non-local deployment.

## Event example
```bash
curl -X POST http://localhost:8000/events \
 -H 'Content-Type: application/json' -H 'X-API-Key: local-dev-key' \
 -d '{"source_id":"acoustic-04","modality":"acoustic","event_type":"possible_gunshot","latitude":-1.4,"longitude":36.8,"confidence":0.87,"severity":5,"synthetic":true}'
```

## Architecture
`Sensor/imagery adapter → signed/authorized ingestion API → validation & dedupe → correlation/triage → human incident review → ranger assignment / approved observation mission → audit log`.

**Risk model:** classify severity independently of model confidence. A P1 alert signals *potential* urgency, never certainty of criminal activity. Camera/drone observations must not be used as automated enforcement decisions.

## Current limitations
Backend state is in memory and resets on restart. Dashboard map uses OpenStreetMap tiles via Leaflet and therefore needs an internet connection for tiles. No geospatial database, external notification delivery, satellite download, physical sensor drivers, drone flight controller integration, user identity provider, device attestation, end-to-end encrypted messaging, or production-grade evidence vault is implemented. The API key is a development-only substitute for real authentication.

## Production roadmap
1. PostgreSQL/PostGIS, durable event bus, idempotent consumers, encrypted object storage and retention controls.
2. OIDC and multi-tenant RBAC, tenant isolation, device credentials, tamper-proof audit storage.
3. MQTT/LoRaWAN secure telemetry; acoustic classifiers with measured precision/recall and time-synchronized localization.
4. STAC/Sentinel-1/2 ingestion; cloud masking and geospatial change detection; account for revisit delay.
5. Human-controlled, legally permitted drone adapter with geofences, no-fly validation and wildlife disturbance safeguards.
6. Offline-capable Flutter ranger client, alert acknowledgements, escalation, communications testing.
7. Field evaluation with false-alarm rates, localization error, detection latency, operator workload, battery and ecological impacts.

## Responsible use
Protect sensitive species locations, minimize collection of identifiable human imagery, restrict access by organization/role, respect aviation regulations and conservation permits, and require ranger/operator authorization for each flight. **No autonomous pursuit, interception, targeting or punitive action.**
