from src.ftr_network import ftr_network_SgAsNd, ftr_network_SgAsEg

data_dir = 'data/'


print '======get feature of road network for dc======'
from src.constants import (fn_feature_seg_as_node_dc, fn_segments_dc, var_directionality_column_dc,
                           fn_feature_seg_as_edge_dc)

path_ftr_SgAsNd_dc = data_dir + fn_feature_seg_as_node_dc
path_segs_dc = data_dir + fn_segments_dc
path_ftr_SgAsEg_dc = data_dir + fn_feature_seg_as_edge_dc
df_ftr_d_dc = ftr_network_SgAsNd(path_segs_dc, path_ftr_SgAsNd_dc, directionality_column=var_directionality_column_dc)
df_ftr_ud_dc = ftr_network_SgAsEg(path_segs_dc, path_ftr_SgAsEg_dc, directionality_column=var_directionality_column_dc)

print '======get feature of road network for ph======'
from src.constants import (fn_segments_ph, fn_feature_seg_as_node_ph, var_directionality_column_ph,
                           fn_feature_seg_as_edge_ph)

path_ftr_SgAsNd_ph = data_dir + fn_feature_seg_as_node_ph
path_segs_ph = data_dir + fn_segments_ph
path_ftr_SgAsEg_ph = data_dir + fn_feature_seg_as_edge_ph
df_ftr_d_ph = ftr_network_SgAsNd(path_segs_ph, path_ftr_SgAsNd_ph, directionality_column=var_directionality_column_ph)
df_ftr_ud_ph = ftr_network_SgAsEg(path_segs_ph, path_ftr_SgAsEg_ph, directionality_column=var_directionality_column_ph)