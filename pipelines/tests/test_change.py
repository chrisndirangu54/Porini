import numpy as np
import rasterio
from rasterio.transform import from_origin
from tempfile import TemporaryDirectory
from pathlib import Path
from pipelines.satellite_change import run
def test_loss_raster():
    with TemporaryDirectory() as d:
        a=Path(d)/"a.tif";b=Path(d)/"b.tif"
        for path,nir in ((a,.8),(b,.3)):
            with rasterio.open(path,"w",driver="GTiff",height=3,width=3,count=2,
                dtype="float32",crs="EPSG:4326",transform=from_origin(36,-1,0.001,0.001)) as ds:
                ds.write(np.full((3,3),.2,dtype="float32"),1)
                ds.write(np.full((3,3),nir,dtype="float32"),2)
        outcome=run(str(a),str(b),str(Path(d)/"out"))
        assert outcome["vegetation_loss_pixels"]==9
