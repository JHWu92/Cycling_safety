# =========================
# Philly
# =========================
# CRS
epsg_ph = None
# OSM
osm_ph_poly_rid = 188022
fn_city_poly_ph = 'city_poly_ph.geojson'
fn_city_poly_ph_png = fn_city_poly_ph.replace('geojson','png')
fn_osm_raw_ph = 'osm_raw_ph.osm'
fn_osm_db_ph = 'osm_db_ph.sqlite3'
# Segments
# TODO: get segments for philly
fn_segments_ph = 'segments_ph.geojson'
# FourSquare Venues
dir_frsq_raw_venues_ph = 'frsq_raw_venues/ph/'
fn_frsq_venues_ph = 'frsq_venues_ph.geojson'


# =========================
# D.C.
# =========================
# CRS
epsg_dc = 3559
# OSM
osm_dc_poly_rid = 162069
fn_city_poly_dc = 'city_poly_dc.geojson'
fn_city_poly_dc_png = fn_city_poly_dc.replace('geojson','png')
fn_osm_raw_dc = 'osm_raw_dc.osm'
fn_osm_db_dc = 'osm_db_dc.sqlite3'
# Segments
fn_segments_dc = 'segments_dc_opendc.geojson'
# FourSquare Venues
dir_frsq_raw_venues_dc = 'frsq_raw_venues/dc/'
fn_frsq_venues_dc = 'frsq_venues_dc.geojson'
# Poi
fn_poi_frsq_dc = 'poi_frsq_dc.geojson'
fn_poi_osm_dc = 'poi_osm_dc.geojson'

# FourSquare Taxonomy
fn_frsq_taxonomy_json = 'frsq_taxonomy_raw.json'
fn_frsq_taxonomy_csv = 'frsq_taxonomy_parsed.csv'
fn_frsq_taxonomy_tree = 'frsq_taxonomy_tree.txt'

# Poi mapping
fn_mapping_for_fs = 'manual/poi_mapping_for_fs.txt'
fn_mapping_for_osm = 'manual/poi_mapping_for_osm.txt'
var_exclude_category_for_osm = 'exclude'
similar_name_threshold = 0.8  # used in detecting frsq and osm duplicates
no_name_value = -1.0
poi_categories = ['art','outdoors and recreation', 'retail shop', 'professional service', 'food',
                  'nightlife spot','residence','schools&university','cycling facilities','transportation']