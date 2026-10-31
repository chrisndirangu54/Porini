# Sentinel Towers — prototype API

Smart tower registry for optical, infrared, thermal, acoustic, smoke, weather and radar sensors. Observations are review-first and flow through Porini's existing incident correlation and audit system.

## API
- `POST /towers` admin: register tower (name, coordinates, height, power and connectivity)
- `GET /towers` admin/ranger: list towers and last reported health
- `POST /towers/{id}/sensors` admin: register tower sensor
- `GET /towers/{id}/sensors` admin/ranger
- `POST /towers/{id}/health` admin/sensor: report battery, online and temperature
- `POST /towers/{id}/observations` admin/sensor: submit one classified sensor observation
- `GET /towers/{id}/observations` admin/ranger: review observations and linked incidents

## Example
```json
{"name":"North Ridge Tower","latitude":-1.2,"longitude":36.8,"height_m":25,"power_type":"solar","connectivity_type":"lte"}
```
Add a sensor with `{"kind":"acoustic","model":"Field microphone array"}`, then submit:
```json
{"sensor_id":"<sensor UUID>","event_type":"chainsaw_detected","confidence":0.72,"severity":3,"synthetic":true}
```

## Limitations / next work
This branch implements API structures only: no real live feeds, trained AI models, tower hardware, RF triangulation, camera control, dashboard, or notification service. Tower registry and observation metadata are **in-memory and lost on restart**, whereas generated Porini incident events enter its existing store. Positioning uses tower coordinates as an approximate location, **not** verified source localization. Acoustic or infrared detection cannot establish an individual's intent or criminal conduct. Require human validation and applicable privacy, conservation and aviation permissions. Add persistent PostgreSQL/PostGIS models, per-device credentials, data retention, uncertainty-aware localization, secure transport and sensor attestation before production.
