# Integration contracts and validation gates

## Acoustic and camera nodes
POST /events with source_id, modality, event_type, UTC timestamp, lat/lon, model confidence, severity, localization uncertainty and external_id. Device identity, replay defense, inference provenance and signature verification must be added before field use. Acoustic location requires a validated synchronized multi-node estimator, **not** the event coordinate by itself.

## Drones
A request and supervisor decision are non-operational workflow records. Implement vendor/PX4 connections separately, with flight permissions, weather/airspace checks, geofencing, operator preflight approval, collision avoidance, wildlife welfare and emergency return-to-home. Never launch a drone merely because a model emits an event.

## Satellite imagery
Future ingestion should use STAC items, scene acquisition time, sensor resolution, QA masks, licensed footprints, preprocessing provenance and per-model uncertainty. Satellite imagery cannot be represented as live surveillance. Store raster outputs in cloud-optimized GeoTIFF, footprints in PostGIS and links with signed short-lived URLs.

## Conservation privacy
Exact locations of threatened species and ranger positions must not be publicly exposed. Ensure tenant-specific data access, encryption, evidentiary provenance, retention/deletion policies and audit trails before deployment. Do not infer guilt from a model-generated detection.
