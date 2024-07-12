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


def process(
    data_id: str,
    variables_str: str,
    level: str,
    date: str | datetime.datetime,
    domain_path: str,
    output_file_name: str,
    shift: tuple[float, float] = None,
    is_cumulated: bool = False
):
    """
    Download and processes the data from DDS and extract it on a domain for telemac.

    :param data_id: DDS dataid
    :param variables_str: Variables separated by comma
    :param level: level
    :param date: model date
    :param domain_path: path to the domain shapefile
    :param output_file_name: output file name
    :param shift: shift the data by x and y (default: None)
    :param is_cumulated: subtract the previous value for each time step (default: False)
    """
    variables = [var.strip() for var in variables_str.split(',')]

    domain = gpd.read_file(domain_path)
    buffer = 0.1
    bbox_wgs = domain.to_crs('epsg:4326').buffer(buffer).total_bounds

    data = None
    for variable in variables:
        data_var = coverages.get_data(data_id, date, variable, level=level)

        if data is None:
            data = data_var[variable]
        else:
            data += data_var[variable]

    if is_cumulated:
        # subtract the previous value for each time step
        data = data.diff('time')

    all_values = []
    for time in data.time:
        data_at_time = data.sel(time=time)
        values = extract_data_on_bbox(
            data_at_time,
            bbox_wgs,
            domain.crs
        )
        all_values.append(values)

    write_file(all_values, HEADER, output_file_name, shift=shift)


def main():
    parser = argparse.ArgumentParser(
        description='Download data from the DDS and extract it on a domain for telemac'
    )
    # add positional args
    parser.add_argument('data_id', type=str, help='Data id')
    parser.add_argument(
        'variables',
        type=str,
        help='Variable or variables list separated by comma'
    )
    parser.add_argument('level', type=str, help='Level')
    parser.add_argument('date', type=str, help='Date from')
    parser.add_argument('domain', type=str, help='Domain shapefile')
    parser.add_argument('output_file_name', type=str, help='Output file name')
    parser.add_argument('--shift', type=float, nargs=2, default=None,
                        help='Shift the data by x and y')
    parser.add_argument('--is-cumulated', action='store_true',
                        help='Subtract the previous value for each time step')

    args = parser.parse_args()
    process(
        args.data_id,
        args.variables,
        args.level,
        args.date,
        args.domain,
        args.output_file_name,
        args.shift,
        args.is_cumulated
    )


if __name__ == '__main__':
    main()
