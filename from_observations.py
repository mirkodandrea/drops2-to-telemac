import argparse
import datetime

import drops2
import geopandas as gpd
import numpy as np
from drops2 import coverages

from lib import HEADER, extract_data_on_bbox, write_file
from secret import dds_password, dds_server, dds_user

drops2.set_credentials(
    dds_server,
    dds_user,
    dds_password
)


def main(
    data_id: str,
    variable: str,
    level: str,
    date_from: str | datetime.datetime,
    date_to: str | datetime.datetime,
    domain_path: str,
    output_file_name: str,
    shift: tuple[float, float] = None
):
    """
    Main function
    """
    domain = gpd.read_file(domain_path)
    buffer = 0.1
    bbox_wgs = domain.to_crs('epsg:4326').buffer(buffer).total_bounds

    dates = coverages.get_dates(data_id, date_from, date_to)
    dates = np.sort(dates)

    all_values = []
    for d in dates:
        print('downloading', d)
        data = coverages.get_data(data_id, d, variable, level=level)
        data_at_time = data[variable].isel(time=0)
        values = extract_data_on_bbox(data_at_time, bbox_wgs, domain.crs)
        all_values.append(values)

    write_file(all_values, HEADER, output_file_name, shift=shift)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # add positional args
    parser.add_argument('data_id', type=str, help='Data id')
    parser.add_argument('variable', type=str, help='Variable')
    parser.add_argument('level', type=str, help='Level')
    parser.add_argument('date_from', type=str, help='Date from')
    parser.add_argument('date_to', type=str, help='Date to')
    parser.add_argument('domain', type=str, help='Domain shapefile')
    parser.add_argument('output_file_name', type=str, help='Output file name')
    parser.add_argument('--shift', type=float, nargs=2, default=None,
                        help='Shift the data by x and y')
    args = parser.parse_args()
    main(
        args.data_id,
        args.variable,
        args.level,
        args.date_from,
        args.date_to,
        args.domain,
        args.output_file_name,
        args.shift
    )
