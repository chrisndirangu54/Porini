# Field deployment checklist (not yet production-certified)

## Local persistence
Core events, incidents, missions, assignments and audit are now stored in SQLite with `PORINI_CORE_DB_PATH`. Additional scientific records use `PORINI_DB_PATH`. Back up both and use a single API process; concurrent multi-process API deployment is unsupported.

## MQTT live connection
Install `workers/requirements.txt`. Set `PORINI_MQTT_HOST`, `PORINI_MQTT_USER`, `PORINI_MQTT_PASSWORD`, `PORINI_SENSOR_KEY`, `PORINI_API_URL`; run `python workers/mqtt_bridge.py`. TLS is enforced by the bridge. This transports actual device-reported events but **does not validate their ML accuracy**, sensor identity or trustworthy location. Use mutually authenticated credentials and secure broker ACLs before field use.

## Flutter ranger prototype
`cd ranger-app && flutter create --platforms android,ios . && flutter pub get && flutter run`. Input server URL and ranger key. The client reads live incidents and acknowledges them; it does **not** yet support offline encrypted synchronization, photos, secure messaging or SOS delivery.

## Before handling sensitive field data
Replace shared API keys with scoped OIDC/device certs, enforce HTTPS, migrate to Postgres/PostGIS, protect endangered species coordinates, establish legal retention and remote access policies, validate all alert models, and use disaster-recovery backups.

## No flight execution
The mission API is an approval ledger, not a PX4 flight adapter. Certified operators must manually execute any permitted flight in approved software; no autonomous intervention or tracking of people is provided.
