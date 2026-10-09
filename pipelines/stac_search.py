"""Search actual remote STAC metadata; downloading remains explicitly controlled."""
import argparse,json
from pystac_client import Client
def search(url,collection,bbox,limit=10):
    catalog=Client.open(url)
    items=catalog.search(collections=[collection],bbox=bbox,max_items=limit).items()
    return [{"id":item.id,"datetime":item.datetime.isoformat() if item.datetime else None,
             "assets":{k:v.href for k,v in item.assets.items()},"bbox":item.bbox} for item in items]
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("catalog");p.add_argument("collection");p.add_argument("--bbox",nargs=4,type=float,required=True);a=p.parse_args()
    print(json.dumps(search(a.catalog,a.collection,a.bbox),indent=2))
