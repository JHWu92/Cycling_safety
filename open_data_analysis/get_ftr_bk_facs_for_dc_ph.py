# coding=utf-8

from src.geom_helper import bfr_20m
from src.ftr_bk_facs import get_feature_bk_facs


data_dir = 'data/'


print """
# =========================
# D.C.
# =========================
"""
from src.constants import fn_osm_db_dc, fn_segments_dc, epsg_dc, fn_feature_bk_facs_dc
path_osm_db_dc = data_dir + fn_osm_db_dc
path_segs_dc = data_dir + fn_segments_dc
path_ftr_dc = data_dir + fn_feature_bk_facs_dc

features_bk_facs_dc = get_feature_bk_facs(path_osm_db_dc, path_segs_dc, path_ftr_dc, epsg_dc, bfr_20m, debug=True)


print """
# =========================
# Philly
# =========================
"""
from src.constants import fn_osm_db_ph, fn_segments_ph, epsg_ph, fn_feature_bk_facs_ph
path_osm_db_ph = data_dir + fn_osm_db_ph
path_segs_ph = data_dir + fn_segments_ph
path_ftr_ph = data_dir + fn_feature_bk_facs_ph

features_bk_facs_ph = get_feature_bk_facs(path_osm_db_ph, path_segs_ph, path_ftr_ph, epsg_ph, bfr_20m, debug=True)
