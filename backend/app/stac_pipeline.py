"""Safely parse saved STAC search results or optional remote STAC via pystac-client.

Remote endpoints must be explicitly allowlisted by administrator; never fetch
arbitrary URLs from HTTP requests. Returns metadata, not wildfire detections.
"""
from datetime import datetime
from urllib.parse import urlparse

def scene_metadata(feature:dict)->dict:
    bbox=feature.get("bbox",[])
    if len(bbox)<4 or not (-180<=bbox[0]<bbox[2]<=180 and -90<=bbox[1]<bbox[3]<=90):
        raise ValueError("Invalid STAC bounding box")
    props=feature.get("properties") or {}
    observed=props.get("datetime") or props.get("start_datetime")
    if not observed:raise ValueError("STAC acquisition time missing")
    dt=datetime.fromisoformat(observed.replace("Z","+00:00"))
    if dt.tzinfo is None: raise ValueError("Acquisition time missing timezone")
    return {
      "item_id":str(feature.get("id","")),"collection":feature.get("collection"),
      "bbox":bbox[:4],"acquired_at":dt.isoformat(),
      "cloud_cover":props.get("eo:cloud_cover"),"assets":list((feature.get("assets") or {}).keys()),
      "status":"metadata_only","fire_confirmed":False,"synthetic":False
    }

def stac_search(catalog_url:str,collection:str,bbox:list[float],allowed_catalogs:list[str],limit:int=10)->list[dict]:
    if catalog_url not in allowed_catalogs:raise ValueError("STAC catalog not allowlisted")
    if not 1<=limit<=50 or len(bbox)!=4:raise ValueError("Invalid query limits")
    u=urlparse(catalog_url)
    if u.scheme!="https" or not u.hostname:raise ValueError("HTTPS STAC URL required")
    try:from pystac_client import Client
    except ImportError as exc:raise RuntimeError("Install optional pystac-client") from exc
    client=Client.open(catalog_url)
    items=client.search(collections=[collection],bbox=bbox,max_items=limit)
    return [scene_metadata(i.to_dict()) for i in items.items()]
