# coding=utf-8

from src.constants import fn_frsq_taxonomy_json, fn_frsq_taxonomy_csv, fn_frsq_taxonomy_tree
from src.constants import fn_city_poly_dc, dir_frsq_raw_venues_dc, fn_frsq_venues_dc
from src.constants import fn_city_poly_ph, dir_frsq_raw_venues_ph, fn_frsq_venues_ph
from src.frsq_helper import *
from src.geom_helper import bfr_20m


# parse FourSquare Taxonomy
data_dir = 'data/'
frsq_taxonomy_json_path = data_dir + fn_frsq_taxonomy_json
frsq_taxonomy_csv_path = data_dir + fn_frsq_taxonomy_csv
frsq_taxonomy_tree_path = data_dir + fn_frsq_taxonomy_tree
parse_frsq_taxonomy(frsq_taxonomy_json_path, frsq_taxonomy_csv_path, frsq_taxonomy_tree_path)


print 'Get FS Venues for dc'
city_dc = data_dir + fn_city_poly_dc
frsq_raw_venues_dc = data_dir + dir_frsq_raw_venues_dc
frsq_venues_in_city_dc = data_dir + fn_frsq_venues_dc

raw_venues_in_city(city_dc, frsq_raw_venues_dc)
show_grids_used(city_dc, frsq_raw_venues_dc)
frsq_venues_in_city_geojson(city_dc, frsq_raw_venues_dc, frsq_venues_in_city_dc)


print ('Get FS Venues for ph')
city_ph = data_dir + fn_city_poly_ph
frsq_raw_venues_ph = data_dir + dir_frsq_raw_venues_ph
frsq_venues_in_city_ph = data_dir + fn_frsq_venues_ph

raw_venues_in_city(city_ph, frsq_raw_venues_ph)
show_grids_used(city_ph, frsq_raw_venues_ph)
frsq_venues_in_city_geojson(city_ph, frsq_raw_venues_ph, frsq_venues_in_city_ph)