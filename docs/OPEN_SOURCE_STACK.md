# Porini — Open-source-first integration policy

Choose open-source tools and inspect **both code and model-weight licenses** before implementation. All integrations remain opt-in.

| Domain | Preferred software | Caveat |
|---|---|---|
| Camera traps | MegaDetector V6 / PyTorch-Wildlife | Model variant licenses differ; use documented weights |
| Species | SpeciesNet | Verify upstream software, weights, and dataset rights |
| Acoustic | BirdNET Analyzer | Model weights CC BY-NC-SA 4.0; commercial deployment needs licensing review |
| Geospatial | PostgreSQL/PostGIS, GDAL, Rasterio, STAC | Provision and validate real data |
| Sensor ingest | MQTT (Mosquitto), NATS | TLS, device credentials and message durability required |
| Identity | Keycloak OIDC | Use verified JWT identity and tenant claims |
| Monitoring | Prometheus + Grafana | Verify license obligations and sensitive data access |
| Offline maps | MapLibre, PMTiles | Respect source tile data licenses and location confidentiality |
| Rangers | Existing Flutter offline application | Needs offline queue/conflict testing |

The `open_source_stack.py` catalog and validation utility list sources and block unreviewed model licenses. They do **not** install packages, provision services, or claim that inference is running.

Commercial/noncommercial distinctions matter: BirdNET software is MIT licensed while its model weights have a noncommercial share-alike license. MegaDetector weights also vary by model variant. Review licenses whenever upstream versions change.

Data-governance controls: minimize ranger/person image retention, protect sensitive species locations, avoid automated enforcement and restrict chemical or drone response to authorized humans.
