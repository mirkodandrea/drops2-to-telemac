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
# Radardaten
#
# Regeln fuer Kommentare
# -	Kommentarzeile < 72 Zeichen
# -	Die Kommentarzeile enth�lt ein #.
# -	Es k�nnen beliebig viele Kommentarzeilen aufeinander folgen.
# -	Die Kommentarzeile steht vor der Datenzeile <t,dt,np> ; d.h. es k�nnen mehre Kommentare im Datensatz verstreut liegen.
# -	Vor oder im Datenblock <x,y,N> darf kein Kommentar stehen.
#
# Zeile <t,dt,np>
# Block mit np-Zeilen <x,y,N> ; x,y in [m] ; N in [mm]
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
    values = data.isel(time=0).values

    # find the indexes of the data that are within the bounding box
    idx = (lats >= bbox_wgs[1]) & (lats <= bbox_wgs[3]) & (
        lons >= bbox_wgs[0]) & (lons <= bbox_wgs[2])
    bounds_values = values[idx]
    bounds_lats = lats[idx]
    bounds_lons = lons[idx]

    transformer = Transformer.from_crs("EPSG:4326", crs)

    output_data = [
        (bounds_values[i], *
         transformer.transform(bounds_lons[i], bounds_lats[i]))
        for i in range(len(bounds_lats))
    ]

    return output_data


def format_values(data: list[tuple], shift: tuple[float, float] = None) -> str:
    """
    Format the data to the required format
    """
    if shift is None:
        shift = (0, 0)

    data_str = '\n'.join(
        [f'{x[1] - shift[0]:.0f}. {x[2] - shift[1]:.0f}. {x[0]:.0f}.' for x in data])
    return data_str


def write_file(
    all_values: list[list[tuple]],
    header: str,
    filename: str,
    shift: tuple[float, float] = None,
    dt: int = 3600
):
    with open(filename, 'w') as f:
        f.write(header)
        for idx, values in enumerate(all_values):
            n_pixels = len(values)
            formatted_values = format_values(values, shift=shift)
            f.write(f'{idx}. {dt}. {n_pixels}\n{formatted_values}\n')


def main(
    date_from: str | datetime.datetime,
    date_to: str | datetime.datetime,
    output_file_name: str,
    shift: tuple[float, float] = None
):
    """
    Main function
    """
    domain = gpd.read_file('data/Dominio_Idraulica_Debed_38N.shp')
    buffer = 0.1
    bbox_wgs = domain.to_crs('epsg:4326').buffer(buffer).total_bounds

    data_id = 'GSMAP'
    variable = 'hourly_rain_rate'

    dates = coverages.get_dates(data_id, date_from, date_to)
    dates = np.sort(dates)

    all_values = []
    for d in dates:
        print('downloading', d)
        data = coverages.get_data(data_id, d, variable, level='0')
        values = extract_data_on_bbox(data[variable], bbox_wgs, domain.crs)
        all_values.append(values)

    write_file(all_values, HEADER, output_file_name, shift=shift)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # add positional args
    parser.add_argument('date_from', type=str, help='Date from')
    parser.add_argument('date_to', type=str, help='Date to')
    parser.add_argument('output_file_name', type=str, help='Output file name')
    parser.add_argument('--shift', type=float, nargs=2, default=None,
                        help='Shift the data by x and y')
    args = parser.parse_args()
    main(args.date_from, args.date_to, args.output_file_name, args.shift)

# %%
