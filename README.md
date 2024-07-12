# TELEMAC data downloader and processor

## Description
This script downloads and processes data from the TELEMAC model. 
The data is downloaded from DDS using Drops2 and processed to be used in the TELEMAC model.

## Configuration
The DDS configuration must be written in the `secret.py` file.
```python
dds_server, dds_user, dds_password = 'http://dds-test.cimafoundation.org/dds/rest', 'user', '***'
```

## Installation
Clone the repo, create a virtual env and install the requirements
```bash
pip install -r requirements.txt
```

## Usage

Example usage for forecast data
```bash
python from_forecast.py --is-cumulated WRF_SUDAN RAINNC,RAINC - 202407110000 data/domain_coarse_citta.shp ./test.dat 
```

Example usage for historical data
```bash
python from_observation.py MODIS RAIN - 202407110000 202407120000 data/domain_coarse_citta.shp ./test.dat 
```