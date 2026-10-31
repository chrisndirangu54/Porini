# Porini FireShield — wildfire decision support

FireShield extends Porini conservation monitoring to wildfire detection, triage and responsible response **without any explosive, pyrotechnic, compressed-gas discharge or automated payload release mechanism**.

## Implemented in this branch
- Existing `POST /events` accepts fire-event observations using the normal sensor/ranger authentication and existing validation, deduplication and incident correlation.
- `GET /fireshield/incidents` lists advisory assessments for recognized fire-event incidents.
- `GET /fireshield/incidents/{incident_id}` returns human-verification requirements, uncertainty, response options and environmental precautions.
- Both endpoints require ranger or admin authorization; no actuator endpoints are added.
- Recognized event types: `wildfire`, `possible_wildfire`, `smoke_detected`, `fire_detected`, `thermal_fire_anomaly`, `vegetation_fire`, `bushfire`.

## Example synthetic event
```bash
curl -X POST http://localhost:8000/events \
  -H 'Content-Type: application/json' -H 'X-API-Key: local-dev-key' \
  -d '{"source_id":"thermal-demo-01","modality":"thermal","event_type":"possible_wildfire","latitude":-1.4,"longitude":36.8,"confidence":0.65,"severity":4,"uncertainty_m":750,"synthetic":true}'
```
Then inspect `GET /fireshield/incidents`.

## Future integrations (not implemented)
1. Geostationary and polar-orbit satellite hotspot feeds with age/quality indicators (e.g. NASA FIRMS, where licensed).
2. Weather, landcover, terrain and fire-spread model ensemble with calibrated uncertainty and independent validation.
3. Camera/thermal/acoustic corroboration and protected-species exposure estimates with location privacy.
4. Fire-authority escalation, acknowledgment and incident command interoperability.
5. A map dashboard and offline ranger app views for fire events.
6. Approved suppression-service integrations **only** through qualified human operators with verified equipment, regulatory permissions and ecological review; no remote release control from Porini.

## Safety boundaries
- Never present model scores as confirmed observations. Synthetic events remain labeled.
- Never automate aircraft dispatch, target acquisition, ignition, chemical reaction or payload discharge.
- Gas-generation capsules are **not** a proposed outdoor suppression technology. Prefer certified firefighting equipment and locally approved agents.
- Avoid dispersing chemicals over sensitive habitats or waterways without an environmental assessment.
- No emergency service deployment is implied by these prototype endpoints.
