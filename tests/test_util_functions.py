from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
import pytest
import rasterio

from aggreunit import raster_to_polygon, join_population_to_shp

BASE = Path(__file__).resolve().parent.joinpath('data')

#----------------INPUT------------------
L1 = BASE.joinpath('abw_subnational_admin_2000_2020.tif')
TABLE = BASE.joinpath('abw_population_2000_2020.csv')
PIXEL = BASE.joinpath('abw_px_area_100m.tif')
#----------------INPUT------------------

#---------------OUTPUT--------------------
L1_SHP = L1.parent.joinpath(f'{L1.stem}.shp')

#---------------OUTPUT--------------------


def test_files_exist():
    assert L1.exists()
    assert TABLE.exists()
    assert PIXEL.exists()

def test_raster_to_polygon():
    gdf = raster_to_polygon(L1)
    src = rasterio.open(L1)
    data = src.read()
    data = data != src.nodata
    units_expected = sorted(list(np.unique(data)))
    units_got = sorted(gdf.adm_id.to_list())
    assert isinstance(gdf, gpd.GeoDataFrame)

def test_raster_to_polygon_save_shp():
    if L1_SHP.exists():
        [x.unlink() for x in BASE.iterdir() if x.stem == L1.stem if not x == L1]
    gdf = raster_to_polygon(L1, L1_SHP)
    gdf_saved = gpd.read_file(L1_SHP)
    gdf_adm = sorted(gdf.adm_id.to_list())
    shp_adm = sorted(gdf_saved.adm_id.to_list())
    assert gdf_adm == shp_adm

def test_join_population_to_shp_with_shp():
    gdf_pop = join_population_to_shp(L1_SHP, TABLE)
    assert isinstance(gdf_pop, gpd.GeoDataFrame)
    assert 'P_2020' in gdf_pop.columns

def test_join_population_to_shp_with_gdf():
    if L1_SHP.exists():
        [x.unlink() for x in BASE.iterdir() if x.stem == L1.stem if not x == L1]
    gdf = raster_to_polygon(L1, L1_SHP)
    gdf_pop = join_population_to_shp(gdf, TABLE, pop_col='P_2019')
    assert isinstance(gdf_pop, gpd.GeoDataFrame)
    assert 'P_2019' in gdf_pop.columns

    



