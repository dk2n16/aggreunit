"""
Helper functions
"""
from pathlib import Path 

import geopandas as gpd
import numpy as np
import pandas as pd
from rasterstats import zonal_stats
import rasterio
from rasterio.features import shapes

def raster_to_polygon(raster, out_shp=None):
    """
    Returns GeoDataFrame of polygonisation of raster and saves GeoDataFrame to out_shp

    Parameters:
    ------------
    raster: (Path/str)
        Path to input raster to polygonise
    out_shp:    (Path/str) - Optional: Default = None
        Path to output polygone shape

    Returns:
    --------
    gdf :   (gpd.GeoDataFrame)
        Geodataframe of polygonised version of input raster 
    """
    mask = None
    with rasterio.Env():
        with rasterio.open(raster) as src:
            image = src.read().astype(np.int32)# first band
            mask = image != src.nodata
            results = ({'properties': {'adm_id': v}, 'geometry': s}   for i, (s, v) in enumerate(shapes(image, mask=mask, transform=src.transform)))
            geoms = list(results)
    gdf = gpd.GeoDataFrame.from_features(geoms, crs='EPSG:4326').dissolve(by='adm_id')
    gdf = gdf.reset_index()
    if out_shp:
        if not out_shp.exists():
            gdf.to_file(out_shp, index=False)
        else:
            raise FileExistsError(f"{out_shp} exists. Please delete before creating new shapefile")
    return gdf

def join_population_to_shp(shp, csv, shp_id='adm_id', csv_id='GID', pop_col='P_2020'):
    """Joins population csv to shapefile and returns geodataframe -- Overwrites input shp (if it's a file and not a dataframe) with population column from table
    
    Parameters:
    ------------
    shp:    (Path/str/GeoDataframe)
        Path to admin unit shapefile or Geodataframe object of shapefile
    csv :   (Path/str)
        Path to population table
    shp_id  :   (str)
        Column in shapefile used for join (Default -> 'adm_id')
    csv_id  :   (str)
        Column in csv used for join (Default -> 'GID')

    """
    if not isinstance(shp, gpd.GeoDataFrame):
        gdf = gpd.read_file(shp)
    else:
        gdf = shp
    gdf = gdf[[x for x in gdf.columns if not x == pop_col]].set_index(shp_id)
    df = pd.read_csv(csv)
    df[shp_id] = df[csv_id]
    df_cols = [shp_id, pop_col]
    df = df[df_cols].set_index(shp_id)
    gdf_pop = gpd.GeoDataFrame(gdf.join(df))
    if not isinstance(shp, gpd.GeoDataFrame):
        gdf_pop.to_file(shp)
    return gdf_pop

#density to gdf
def get_pop_density(shp, raster, out_shp, shp_index_col='adm_id', pop_col='P_2020'):
    """
    Returns Geodataframe of admin units with population density appended

    Parameters:
    -----------
    shp :   (Path/str/gpd.GeoDataFrame)
        Path to/geodataframe of imput geometries
    raster  :   (Path/str)
        Path to pixel area raster
    out_shp :   (Path/str)
        Path to output shapefile
    shp_index_col   :   (str)
        Shape column used in join (Default = 'adm_id')
    pop_col :   (str)
        Population column in shapefile

    Returns:
    --------
    gdf_density :   (gpd.GeoDataFrame)
        Input geodataframe with population density column appended
    """
    if not isinstance(shp, gpd.GeoDataFrame):
        gdf = gpd.read_file(shp)
    else:
        gdf = shp
    gdf = gdf[[x for x in gdf.columns if not x in ['area', 'density', 'sum']]].reset_index()
    gdf_sum = zonal_stats(gdf, raster, stats=['sum'], geojson_out=True)
    gdf_sum = gpd.GeoDataFrame.from_features(gdf_sum, crs="EPSG:4326")[['adm_id', 'sum']]
    gdf_sum['area'] = gdf_sum['sum']
    gdf_density = gpd.GeoDataFrame(gdf.set_index(shp_index_col).join(gdf_sum.set_index(shp_index_col)))
    gdf_density['density'] = gdf_density[pop_col] / gdf_density['area']
    cols = [pop_col, 'area', 'density', 'geometry']
    gdf_density = gdf_density[cols]
    gdf_density.to_file(out_shp)
    return gdf_density

def sort_by_density(gdf):
    """
    Returns gdf sorted by density adds lables and paired (or not) boolean

    Parameters  
    -----------
    gdf :   (gpd.GeoDataFrame)
        Input geodataframe with density value column

    Returns
    --------
    gdf :   (gpd.GeoDataFrame)
        Sorted dataframe (by density) with labels to indicate whether admin unit has been paired yet (all initialised to False)
    """
    gdf = gdf.sort_values(by='density', ascending=False)
    gdf['labels'] = gdf.index
    gdf['paired'] = False
    return gdf

