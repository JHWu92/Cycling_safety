# coding=utf-8

from src.osm.container import OSMContainer
from src.osm.osm_clean import get_city
from src.constants import fn_city_poly_dc, fn_osm_db_dc, fn_osm_raw_dc, fn_city_poly_ph, fn_osm_db_ph, fn_osm_raw_ph
from src.osm.osm2db import build_db_from_osm

data_dir = 'data/'
city_dc = get_city(data_dir+fn_city_poly_dc)
osm_raw_dc = OSMContainer(data_dir + fn_osm_raw_dc)
build_db_from_osm(osm_raw_dc, city_dc, data_dir + fn_osm_db_dc)

city_ph = get_city(data_dir+fn_city_poly_ph)
osm_raw_ph = OSMContainer(data_dir + fn_osm_raw_ph)
build_db_from_osm(osm_raw_ph, city_ph, data_dir + fn_osm_db_ph)