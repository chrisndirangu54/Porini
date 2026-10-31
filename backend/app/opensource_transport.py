"""Opt-in PostGIS persistence and NATS publish (no silent fallback)."""
import json
import os
import uuid

def insert_observation(event: dict, dsn: str | None = None) -> str:
    dsn=dsn or os.getenv("POSTGIS_DSN")
    if not dsn: raise RuntimeError("POSTGIS_DSN not configured")
    import psycopg
    tenant=event.get("tenant_id")
    if not tenant:raise ValueError("tenant_id required")
    lat=float(event["latitude"]);lon=float(event["longitude"])
    if not -90<=lat<=90 or not -180<=lon<=180:raise ValueError("Coordinates out of bounds")
    observation_id=str(uuid.uuid4())
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO conservation_observations
                (id,tenant_id,source_id,modality,event_type,observed_at,
                 geom,uncertainty_m,confidence,synthetic,model_id,metadata)
                VALUES (%s,%s,%s,%s,%s,%s,ST_SetSRID(ST_MakePoint(%s,%s),4326)::geography,
                        %s,%s,%s,%s,%s::jsonb)""",
                (observation_id,tenant,event["source_id"],event["modality"],event["event_type"],
                 event["observed_at"],lon,lat,event.get("uncertainty_m"),event["confidence"],
                 event.get("synthetic",False),event.get("model_id"),json.dumps(event.get("metadata",{}))))
    return observation_id

async def publish_observation(event: dict, url: str | None = None)->str:
    url=url or os.getenv("PORINI_NATS_URL")
    if not url:raise RuntimeError("PORINI_NATS_URL not configured")
    import nats
    nc=await nats.connect(servers=[url],connect_timeout=3,max_reconnect_attempts=0)
    try:
        js=nc.jetstream()
        tenant=event.get("tenant_id")
        if not tenant or not tenant.replace("-","").replace("_","").isalnum():
            raise ValueError("Invalid tenant identifier")
        payload=json.dumps(event,allow_nan=False).encode("utf-8")
        ack=await js.publish("porini.observations."+tenant,payload)
        return str(ack.seq)
    finally:
        await nc.drain()
