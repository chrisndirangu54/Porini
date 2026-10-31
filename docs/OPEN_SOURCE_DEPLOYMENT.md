# Open-source development stack

Use `docker compose -f compose.opensource.yml config` then `docker compose -f compose.opensource.yml up -d` after setting the three required passwords in a private `.env`. No external credentials or weights are bundled.

The stack provisions PostGIS, NATS JetStream, Mosquitto, Prometheus, Grafana and Keycloak **as optional, isolated development services**. They do not automatically wire into the Porini API. In particular, only Keycloak's development login is localhost-bound. Do not expose any other container ports until TLS, firewall rules, tenant isolation and service accounts are configured.

**Mosquitto:** anonymous auth is disabled. Provision users/password file and an appropriately scoped authenticated network listener prior to ingestion. No MQTT messaging is functional in the base configuration.

**Identity:** Keycloak is in insecure `start-dev` mode. Before deployment use production mode with TLS, configured realm, issuer/audience/JWKS, OIDC claims and stable `sub` identity. Review API decisions require `PORINI_AUTH_MODE=oidc`.

**Storage:** PostGIS bootstrap schema applies only on fresh empty DB volume. An existing DB requires explicit migrations and backups. Current Porini application remains on SQLite unless migrated. PostgreSQL data credentials must stay private.

**Monitoring:** Prometheus initially scrapes only itself; add authenticated services and privacy-aware dashboards later.

**Models:** no wildlife weights are fetched, no AI metrics claimed, and no sensor feeds are connected. Licensing must be checked separately for software, weights and data.
