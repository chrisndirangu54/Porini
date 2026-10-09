# Satellite and geospatial pipeline

Data sources: Copernicus Sentinel-1 radar, Sentinel-2 optical, USGS Landsat, NASA FIRMS active fire products, STAC APIs and optional licensed commercial scenes.

Open source: pystac-client, stackstac, rasterio, xarray, rioxarray, GDAL, geopandas, shapely, torchgeo, Orfeo Toolbox, QGIS, PostGIS and TiTiler.

A typed STAC scene metadata validator is implemented in `backend/app/imagery.py`. **No actual satellite scene is downloaded and no real change detection is computed yet.** Production workers should persist acquisition date, processing lineage, QA masks, spatial resolution, cloud cover, model version, uncertainty and license.

Suggested pipeline: STAC search -> consent/license + AOI -> asset download -> QA/cloud mask -> coregistration -> change baseline -> segmentation/change inference -> polygon validation -> human review -> verified incident.
