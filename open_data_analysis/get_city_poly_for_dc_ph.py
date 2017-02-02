# coding=utf-8
import geopandas as gp

from src.osm.container import OSMContainer
from src.osm.osm2shp import rltn2shps
from src.constants import osm_ph_poly_rid, fn_osm_raw_ph, fn_city_poly_ph, fn_city_poly_ph_png
from src.constants import osm_dc_poly_rid, fn_osm_raw_dc, fn_city_poly_dc, fn_city_poly_dc_png


def get_city_poly(osm_city_rid, osm_raw_path, city_poly_path, city_poly_png_path):
    osm_raw = OSMContainer(osm_raw_path)
    poly_ph = rltn2shps(osm_raw, osm_raw.get_osm_relation_by_id(osm_city_rid))['Polygon'][0]
    gpdf = gp.GeoDataFrame([poly_ph], columns=['geometry'])
    gpdf.crs = {'init': 'epsg:4326'}
    with open(city_poly_path, 'w') as f:
        f.write(gpdf.to_json())
    ax = gpdf.plot(figsize=(20,20))
    fig = ax.get_figure()
    fig.savefig(city_poly_png_path)


data_dir = 'data/'
# paths for ph
osm_raw_ph = data_dir + fn_osm_raw_ph
city_poly_ph = data_dir + fn_city_poly_ph
city_poly_ph_png = data_dir + fn_city_poly_ph_png
get_city_poly(osm_ph_poly_rid, osm_raw_ph, city_poly_ph, city_poly_ph_png)

# paths for dc
osm_raw_dc = data_dir + fn_osm_raw_dc
city_poly_dc = data_dir + fn_city_poly_dc
city_poly_dc_png = data_dir + fn_city_poly_dc_png
get_city_poly(osm_dc_poly_rid, osm_raw_dc, city_poly_dc, city_poly_dc_png)

