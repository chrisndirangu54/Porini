"""Open-source integration catalog: metadata and license gates, no implicit deployment."""
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Component:
    name: str
    function: str
    source: str
    software_license: str
    model_license: str | None = None
    deployment: str = "optional_not_configured"
    review_required: bool = True

COMPONENTS={
 "megadetector_v6":Component("MegaDetector V6","Camera-trap animal/person/vehicle detection","https://github.com/microsoft/MegaDetector","MIT code","variant-specific: MIT/Apache-2.0/AGPL-3.0"),
 "speciesnet":Component("SpeciesNet","Species classification","https://github.com/google/cameratrapai","verify current upstream license","verify weights and dependencies"),
 "birdnet":Component("BirdNET Analyzer","Bird acoustic classification","https://github.com/birdnet-team/BirdNET-Analyzer","MIT","CC BY-NC-SA 4.0 (noncommercial models)"),
 "postgis":Component("PostGIS","Spatial database","https://postgis.net/","GPL-2.0-or-later"),
 "gdal":Component("GDAL","Raster processing","https://gdal.org/","MIT/X"),
 "pystac":Component("pystac-client","STAC discovery","https://github.com/stac-utils/pystac-client","Apache-2.0"),
 "nats":Component("NATS","Event messaging","https://github.com/nats-io/nats-server","Apache-2.0"),
 "mosquitto":Component("Eclipse Mosquitto","MQTT broker","https://mosquitto.org/","EPL-2.0 / EDL-1.0"),
 "keycloak":Component("Keycloak","OIDC identity","https://www.keycloak.org/","Apache-2.0"),
 "grafana":Component("Grafana","Operations observability","https://grafana.com/oss/grafana/","AGPL-3.0"),
}
def catalog():
    return {"components":{k:asdict(v) for k,v in COMPONENTS.items()},
            "auto_download_enabled":False,"license_approval_required":True,
            "external_credentials_configured":False,"production_ready":False}
def validate_selection(selection:list[str],approved_licenses:list[str])->dict:
    unknown=[x for x in selection if x not in COMPONENTS]
    restricted=[x for x in selection if x in COMPONENTS and COMPONENTS[x].model_license and
                x not in approved_licenses]
    return {"unknown":unknown,"license_review_pending":restricted,
            "eligible_for_configuration":not unknown and not restricted,
            "automatically_installed":False}
