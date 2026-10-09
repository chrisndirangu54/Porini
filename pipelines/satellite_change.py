"""Runnable co-registered multispectral GeoTIFF NDVI loss analysis.

Both scenes must be reflectance-calibrated and accompanied by QA masks for scientific usage.
Outputs float NDVI change and uint8 vegetation-loss mask GeoTIFF; not an instant alert.
"""
import argparse
import numpy as np
import rasterio
from rasterio.warp import reproject,Resampling
def run(before,after,out_prefix,red_band=1,nir_band=2,threshold=-0.2,minimum_ndvi=0.3):
    with rasterio.open(before) as a,rasterio.open(after) as b:
        if not a.crs or not b.crs:raise ValueError("Both scenes need a valid CRS")
        if a.count<max(red_band,nir_band) or b.count<max(red_band,nir_band):raise ValueError("Band index outside source")
        red0=a.read(red_band).astype("float32");nir0=a.read(nir_band).astype("float32")
        red1=np.full(red0.shape,np.nan,dtype="float32")
        nir1=np.full(red0.shape,np.nan,dtype="float32")
        for band,dest in [(red_band,red1),(nir_band,nir1)]:
            reproject(source=rasterio.band(b,band),destination=dest,src_transform=b.transform,src_crs=b.crs,dst_transform=a.transform,dst_crs=a.crs,src_nodata=b.nodata,dst_nodata=np.nan,resampling=Resampling.bilinear)
        valid=np.isfinite(red0)&np.isfinite(nir0)&np.isfinite(red1)&np.isfinite(nir1)
        if a.nodata is not None: valid &= (red0!=a.nodata)&(nir0!=a.nodata)
        valid &= (nir0+red0)>0
        valid &= (nir1+red1)>0
        old=np.full(red0.shape,np.nan,dtype="float32")
        new=np.full(red0.shape,np.nan,dtype="float32")
        old[valid]=(nir0[valid]-red0[valid])/(nir0[valid]+red0[valid])
        new[valid]=(nir1[valid]-red1[valid])/(nir1[valid]+red1[valid])
        change=new-old
        loss=((old>=minimum_ndvi)&(change<=threshold)&valid).astype("uint8")
        profile=a.profile.copy()
        profile.update(count=1,dtype="float32",nodata=-9999,compress="deflate")
        with rasterio.open(out_prefix+"_ndvi_change.tif","w",**profile) as dst:dst.write(np.where(valid,change,-9999),1)
        profile.update(dtype="uint8",nodata=255)
        with rasterio.open(out_prefix+"_vegetation_loss.tif","w",**profile) as dst:dst.write(np.where(valid,loss,255).astype("uint8"),1)
        return {"valid_pixels":int(valid.sum()),"vegetation_loss_pixels":int(loss.sum()),"loss_fraction":float(loss.sum()/max(1,valid.sum())),
                "limitations":"Cloud and shadow masking, sensor calibration, seasonality and field verification are required"}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("before");p.add_argument("after");p.add_argument("--out-prefix",default="change")
    p.add_argument("--red-band",type=int,default=1);p.add_argument("--nir-band",type=int,default=2)
    args=p.parse_args();print(run(args.before,args.after,args.out_prefix,args.red_band,args.nir_band))
