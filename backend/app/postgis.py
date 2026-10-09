"""Real PostGIS-backed interoperable observations. Connect with POSTGIS_DSN."""
import os
from contextlib import contextmanager
@contextmanager
def connect():
    import psycopg
    dsn=os.environ["POSTGIS_DSN"]
    with psycopg.connect(dsn) as db:yield db
def init():
    with connect() as db:
        db.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        db.execute("""CREATE TABLE IF NOT EXISTS geospatial_events(
            id UUID PRIMARY KEY, tenant_id TEXT NOT NULL, modality TEXT NOT NULL,
            event_type TEXT NOT NULL, observed_at TIMESTAMPTZ NOT NULL,
            confidence DOUBLE PRECISION CHECK (confidence BETWEEN 0 AND 1),
            severity INT CHECK(severity BETWEEN 1 AND 5),
            synthetic BOOLEAN NOT NULL, geom GEOGRAPHY(POINT,4326) NOT NULL,
            attributes JSONB NOT NULL DEFAULT '{}')""")
        db.execute("CREATE INDEX IF NOT EXISTS idx_geo_events_geom ON geospatial_events USING GIST(geom)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_geo_events_tenant_time ON geospatial_events(tenant_id,observed_at DESC)")
def insert_event(event,tenant):
    with connect() as db:
        db.execute("""INSERT INTO geospatial_events(id,tenant_id,modality,event_type,observed_at,
            confidence,severity,synthetic,geom,attributes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,ST_SetSRID(ST_MakePoint(%s,%s),4326)::geography,%s::jsonb)
            ON CONFLICT(id) DO NOTHING""",(event.id,tenant,event.modality.value,event.event_type,event.timestamp,
            event.confidence,event.severity,event.synthetic,event.longitude,event.latitude,"{}"))
