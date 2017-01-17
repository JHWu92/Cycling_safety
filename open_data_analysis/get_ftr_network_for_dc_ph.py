from src.ftr_network import ftr_network_SgAsNd
data_dir = 'data/'

from src.constants import fn_feature_seg_as_node_dc, fn_segments_dc, var_directionality_column_dc
print '======get feature of road network for dc======'
path_ftr_SgAsNd_dc = data_dir + fn_feature_seg_as_node_dc
path_segs_dc = data_dir + fn_segments_dc
ftr_network_SgAsNd(path_segs_dc, path_ftr_SgAsNd_dc, var_directionality_column_dc, True)


from src.constants import fn_segments_ph, fn_feature_seg_as_node_ph, var_directionality_column_ph
print '======get feature of road network for ph======'
path_ftr_SgAsNd_ph = data_dir + fn_feature_seg_as_node_ph
path_segs_ph = data_dir + fn_segments_ph
ftr_network_SgAsNd(path_segs_ph, path_ftr_SgAsNd_ph, var_directionality_column_ph, True)