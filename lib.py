# %%
import argparse
import datetime
from secret import dds_password, dds_server, dds_user

import drops2
import geopandas as gpd
import numpy as np
import xarray as xr
from drops2 import coverages
from pyproj import CRS, Transformer

drops2.set_credentials(
    dds_server,
    dds_user,
    dds_password
)


HEADER = '''
#
'''


def extract_data_on_bbox(
        data: xr.DataArray,
        bbox_wgs: tuple[float, float, float, float],
        crs: CRS) -> list[tuple]:
    """
    Extract the data that is within the bounding box and
    convert the lat lon to the domain crs
    """
    lats = data['latitude'].values
    lons = data['longitude'].values
    values = data.values

    # find the indexes of the data that are within the bounding box
    idx = (lats >= bbox_wgs[1]) & (lats <= bbox_wgs[3]) & (
        lons >= bbox_wgs[0]) & (lons <= bbox_wgs[2])
    bounds_values = values[idx]
    bounds_lats = lats[idx]
    bounds_lons = lons[idx]

    transformer = Transformer.from_crs("EPSG:4326", crs)

    output_data = [
        (bounds_values[i], *
         transformer.transform(bounds_lats[i], bounds_lons[i]))
        for i in range(len(bounds_lats))
    ]

    return output_data


def write_file(
    all_values: list[list[tuple]],
    header: str,
    filename: str,
    shift: tuple[float, float] = None,
    dt: int = 3600
):
    if shift is None:
        shift = (0, 0)

    with open(filename, 'w') as f:
        f.write(header)
        first = all_values[0]
        n_times = len(all_values)
        n_pixels = len(first)
        f.write(f'{n_pixels},{n_times}\n')
        for _v, x, y in first:
            f.write(f'{(x- shift[0]):.0f},{(y- shift[1]):.0f}\n')
        for idx, values in enumerate(all_values):
            formatted_values = ','.join([f'{v[0]:.2f}' for v in values])
            f.write(f'{idx * dt},{formatted_values}\n')
