from pathlib import Path

import pytest

from aggreunit import raster_to_polygon

BASE = Path(__file__).resolve().parent.joinpath('data')
L1 = BASE.joinpath('abw_subnational_admin_2000_2020.tif')
TABLE = BASE.joinpath('abw_population_2000_2020.csv')
PIXEL = BASE.joinpath('abw_px_area_100m.tif')