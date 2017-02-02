# coding=utf-8
from src.constants import fn_mapping_for_fs, fn_mapping_for_osm
from src.geom_helper import bfr_20m
from src.ftr_poi import get_feature_poi

bfr_func = bfr_20m
pts_bfr_range = 5

data_dir = 'data/'
path_mapping_for_fs = data_dir+fn_mapping_for_fs
path_mapping_for_osm = data_dir+fn_mapping_for_osm


# =========================
# D.C.
# =========================
# data file name for dc
from src.constants import fn_frsq_venues_dc, fn_segments_dc, epsg_dc, fn_osm_db_dc
path_frsq_venues_dc = data_dir + fn_frsq_venues_dc
path_osm_db_dc = data_dir + fn_osm_db_dc
path_segs_dc = data_dir + fn_segments_dc

# output statistics of poi for dc
from src.constants import fn_poi_distr_dc, fn_feature_poi_dc, fn_poi_seg_cvrg_dc, fn_poi_boxplot_per_seg_dc
path_poi_distr_dc = data_dir + fn_poi_distr_dc
path_feature_poi_dc = data_dir + fn_feature_poi_dc
path_poi_seg_cvrg_dc = data_dir + fn_poi_seg_cvrg_dc
path_poi_boxplot_per_seg_dc = data_dir + fn_poi_boxplot_per_seg_dc

# get feature POI for dc
seg_poi_features_dc, poi_distr_dc, poi_near_segs_dc, seg_poi_index_dc = get_feature_poi(
    path_frsq_venues_dc, path_osm_db_dc, path_segs_dc, path_mapping_for_fs, path_mapping_for_osm, path_poi_distr_dc,
    path_feature_poi_dc, path_poi_seg_cvrg_dc, path_poi_boxplot_per_seg_dc,
    bfr_func, pts_bfr_range, bfr_crs=epsg_dc, init_crs=4326, debug=True)


# =========================
# Philly
# =========================
# data file name for ph
from src.constants import fn_frsq_venues_ph, fn_segments_ph, epsg_ph, fn_osm_db_ph
path_frsq_venues_ph = data_dir + fn_frsq_venues_ph
path_osm_db_ph = data_dir + fn_osm_db_ph
path_segs_ph = data_dir + fn_segments_ph

# output statistics of poi for ph
from src.constants import fn_poi_distr_ph, fn_feature_poi_ph, fn_poi_seg_cvrg_ph, fn_poi_boxplot_per_seg_ph
path_poi_distr_ph = data_dir + fn_poi_distr_ph
path_feature_poi_ph = data_dir + fn_feature_poi_ph
path_poi_seg_cvrg_ph = data_dir + fn_poi_seg_cvrg_ph
path_poi_boxplot_per_seg_ph = data_dir + fn_poi_boxplot_per_seg_ph

# get feature POI for ph
seg_poi_features_ph, poi_distr_ph, poi_near_segs_ph, seg_poi_index_ph = get_feature_poi(
    path_frsq_venues_ph, path_osm_db_ph, path_segs_ph, path_mapping_for_fs, path_mapping_for_osm, path_poi_distr_ph,
    path_feature_poi_ph, path_poi_seg_cvrg_ph, path_poi_boxplot_per_seg_ph,
    bfr_func, pts_bfr_range, bfr_crs=epsg_ph, init_crs=4326, debug=True)