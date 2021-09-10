from pathlib import Path
import geopandas as gpd
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
import pytest
import rasterio

from aggreunit import AggregateUnits

BASE = Path(__file__).resolve().parent.joinpath('tests/data/integration_data')

#----------------INPUT------------------
L1 = BASE.joinpath('ABW_L1_mastergrid.tif') # mastergrid
TABLE = BASE.joinpath('ABW_pop.csv') # pop table
PIXEL = BASE.joinpath('ABW_PixelArea_WPGP.tif') # pixel area
#----------------INPUT------------------

#---------------OUTPUT--------------------
L1_SHP = L1.parent.joinpath(f'{L1.stem}.shp')
TABLE_AGGR = TABLE.parent.joinpath(f'{TABLE.stem}_A.csv') # aggregated csv
L1_SHP_AGGR = L1.parent.joinpath(f'{L1_SHP.stem}_A.shp') # Aggregated shapefile
L1_A = L1.parent.joinpath(f'{L1.stem}_A.tif') # aggregated raster

if __name__ == "__main__":
    if L1_SHP.exists():
        [x.unlink() for x in BASE.iterdir() if x.name.startswith(L1.stem) if not x.name.endswith('.tif')]
    x = AggregateUnits(L1, TABLE, PIXEL, L1_A, TABLE_AGGR, L1_SHP_AGGR, save_admin_shape=True)
    x._aggregate()