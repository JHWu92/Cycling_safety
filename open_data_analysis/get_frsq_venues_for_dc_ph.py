# coding=utf-8

from src.constants import fn_city_poly_dc, dir_frsq_raw_venues_dc, fn_frsq_venues_dc
from src.constants import fn_city_poly_ph, dir_frsq_raw_venues_ph, fn_frsq_venues_ph
from src.frsq_helper import *

data_dir = 'data/'

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