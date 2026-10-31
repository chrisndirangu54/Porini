-- Apply only on PostgreSQL with PostGIS installed. Review permissions beforehand.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE TABLE IF NOT EXISTS conservation_observations (
 id UUID PRIMARY KEY,
 tenant_id TEXT NOT NULL,
 source_id TEXT NOT NULL,
 modality TEXT NOT NULL,
 event_type TEXT NOT NULL,
 observed_at TIMESTAMPTZ NOT NULL,
 ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 geom GEOGRAPHY(POINT,4326),
 uncertainty_m DOUBLE PRECISION CHECK(uncertainty_m >= 0),
 confidence DOUBLE PRECISION CHECK(confidence >= 0 AND confidence <= 1),
 synthetic BOOLEAN NOT NULL,
 model_id TEXT,
 verified_by TEXT,
 evidence_hash TEXT,
 metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS observations_tenant_time_idx ON conservation_observations (tenant_id,observed_at DESC);
CREATE INDEX IF NOT EXISTS observations_spatial_idx ON conservation_observations USING GIST (geom);
CREATE INDEX IF NOT EXISTS observations_event_idx ON conservation_observations (tenant_id,event_type);
