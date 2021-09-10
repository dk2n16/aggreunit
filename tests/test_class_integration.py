import pytest
from pathlib import Path
import geopandas as gpd
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
import pytest
import rasterio

from aggreunit import AggregateUnits

BASE = Path(__file__).resolve().parent.joinpath('data/integration_data')

#----------------INPUT------------------
L1 = BASE.joinpath('ABW_L1_mastergrid.tif')
TABLE = BASE.joinpath('ABW_pop.csv')
PIXEL = BASE.joinpath('ABW_PixelArea_WPGP.tif')
#----------------INPUT------------------

#---------------OUTPUT--------------------
L1_SHP = L1.parent.joinpath(f'{L1.stem}.shp')
TABLE_AGGR = TABLE.parent.joinpath(f'{TABLE.stem}_A.csv')
L1_SHP_AGGR = L1.parent.joinpath(f'{L1_SHP.stem}_A.shp')
L1_A = L1.parent.joinpath(f'{L1.stem}_A.tif')

#---------------OUTPUT--------------------

@pytest.fixture
def agg():
    if L1_SHP.exists():
        [x.unlink() for x in BASE.iterdir() if x.name.startswith(L1.stem) if not x.name.endswith('.tif')]
    x = AggregateUnits(L1, TABLE, PIXEL, L1_A, TABLE_AGGR, L1_SHP_AGGR, save_admin_shape=True)
    yield x

def test_instantiation_of_class(agg):
    assert isinstance(agg, AggregateUnits)

def test_data_processed(agg):
    agg._aggregate()
    assert L1_A.exists()
    assert L1_SHP_AGGR.exists()
    assert TABLE_AGGR.exists()





