# Optional real open-source integrations

The `backend/app/opensource_transport.py` functions perform real PostGIS writes using parameterized SQL and NATS JetStream publication **when explicitly called with configured services**. No fake persistence acknowledgments are returned.

Install optional extras `psycopg[binary]`, `nats-py`, and `pytest-asyncio`. PostGIS schema must be migrated before insertion; JetStream stream covering `porini.observations.*` must be provisioned before publishing. Use network-isolated credentials and secrets outside source control.

**Important:** The app's existing `POST /events` path still writes to its current SQLite store. This new module is an opt-in adapter, not yet an atomic dual-write integration. A production migration needs a transaction-backed outbox to prevent events being saved in one store and lost in the other. Never represent this as live end-to-end integration until that change and fault-injection tests are completed.

For production enforce DB row-level security per tenant, verified identity-to-tenant binding, encrypted evidence storage, service authentication, NATS accounts and publication ACLs, and database migration/rollback procedures.
