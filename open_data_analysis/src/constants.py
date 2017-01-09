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
fn_poi_distr_dc = 'poi_distr_dc.csv'
fn_poi_seg_cvrg_dc = 'poi_seg_coverage_dc.html'
fn_poi_boxplot_per_seg_dc = 'poi_boxplot_per_seg_dc.html'
fn_feature_poi_dc = 'feature_poi_dc.csv'

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

# Bike facilities
# TODO: highway='footway', footway=sidewalk
tag_for_pattern = ['highway', 'cycleway', 'cycleway:left', 'cycleway:right', 'cycleway:both',
     'oneway:bicycle', 'bicycle', 'bicycle:lanes', 'bicycle:backward',
     'amenity', 'foot', 'sidewalk','oneway','lanes']
feature_bk_facs = ['cycle_lane', 'is_shared', 'cycle_way', 'side_walk', 'bikable']
# used in producing bk facilities patterns, in developing bk facs assignment rules.ipynb
bk_type = {
    'L1a_1': [('highway','*'), ('cycleway','lane')],
    'L1a_2': [('highway','*'),('cycleway:left','lane'),('cycleway:right','lane'),],
    'L1a_3': [('highway','*'),('cycleway:both','lane'),],
    'L1b_1': [('highway','*'),('cycleway:right','lane'),('oneway:bicycle','no')],
    'L1b_2': [('highway','*'), ('cycleway','lane')],
    'L2': [('highway','*'),('cycleway:right','lane'),('-oneway:bicycle','no')],
    'M1_1': [('highway','*'),('oneway','yes'),('cycleway','lane'),('oneway:bicycle','no')],
    'M1_2': [('highway','*'),('oneway','yes'),('cycleway:left','opposite_lane'),('cycleway:right','lane')],
    'M2a_1': [('highway','*'),('oneway','yes'),('cycleway:right','lane')],
    'M2a_2': [('highway','*'),('oneway','yes'),('cycleway','lane')],
    'M2b_1': [('highway','*'),('oneway','yes'),('cycleway:left','lane'),('-oneway:bicycle','no')],
    'M2b_2': [('highway','*'),('oneway','yes'),('cycleway','lane')],
    'M2c': [('highway','*'),('oneway','yes'),('cycleway','lane'),('lanes',['2',2])],
    'M2d': [('highway','*'),('oneway','yes'),('cycleway:left','lane'),('oneway:bicycle','no'),],
    'M3a_1': [('highway','*'), ('oneway','yes'),('oneway:bicycle','no'),('cycleway:left','opposite_lane')],
    'M3a_2': [('highway','*'), ('oneway','yes'),('oneway:bicycle','no'),('cycleway','opposite_lane')],
    'M3b_1': [('highway','*'), ('oneway','yes'),('oneway:bicycle','no'),('cycleway:right','opposite_lane')],
    'M3b_2': [('highway','*'), ('oneway','yes'),('oneway:bicycle','no'),('cycleway','opposite_lane')],
    'M4_1': [('highway','*'),('oneway','yes'),('cycleway:right','lane')],
    'M4_2': [('highway','*'),('oneway','yes'),('cycleway','lane')],
    'M4_3': [('highway','*'), ('cycleway','lane')],
    'M4_4': [('highway','*'),('cycleway:left','lane'),('cycleway:right','lane'),],
    'M4_5': [('highway','*'),('cycleway:both','lane'),],

    'T1_1':[('highway','*'),('bicycle','use_sidepath')],
    'T1_2':[('highway','cycleway'),('oneway','yes')],
    'T1_3':[('highway','*'),('cycleway','track')],
    'T2_1':[('highway','*'),('bicycle','use_sidepath')],
    'T2_2':[('highway','cycleway'),('oneway','no')],
    'T2_3':[('highway','*'),('cycleway:right','track')],

    'T3_1':[('highway','*'),('bicycle','use_sidepath')],
    'T3_2':[('highway','cycleway'),('oneway','no')],
    'T3_3':[('highway','*'),('oneway','yes'),('cycleway:right','track'),('oneway:bicycle','no')],

    'T4_1':[('highway','*'),('bicycle','use_sidepath')],
    'T4_2':[('highway','cycleway'),('oneway','yes')],
    'T4_3':[('highway','*'),('cycleway:right','track')],

    'S1_1':[('highway','*'),('oneway','yes'),('oneway:bicycle','no')],
    'S1_2':[('highway','*'),('oneway','yes'),('cycleway','opposite')],


    'foot':[('highway','footway'),],
    'pedestrian': [('highway','pedestrian'),],
    'sidewalk':[('sidewalk','*'),],
    'M2d_my': [('highway','service'), ('cycleway:left','opposite_lane'), ('oneway','yes')],
    'M1_my':[('highway','secondary'), ('cycleway','opposite_lane'), ('bicycle','designated'), ('oneway','yes'), ('lanes','1')]

}