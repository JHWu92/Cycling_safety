# coding=utf-8
def get_feature_bk_facs(path_osm_db, path_segs, path_ftr_bk_facs, bfr_crs, bfr_func, init_crs=4326, debug=False):
    """
    :return: pandas.DataFrame, columns = [index_seg, cycle_lane,is_shared,cycle_way,side_walk,bikable]
    """
    from osm.bk_facs_rules import ftr_func
    from osm.osmdb_filter import select_bk_facs_with_geom
    from constants import tag_for_pattern, ftr_name_bk_facs, index_seg, index_ln
    from geom_helper import lns_polys2lns
    import geopandas as gp
    import pandas as pd

    bk_facs = select_bk_facs_with_geom(path_osm_db, ot='W')
    for t in tag_for_pattern:
        bk_facs[t] = bk_facs.tags.apply(lambda x: x.get(t,''))
    for ftr in ftr_name_bk_facs:
        bk_facs[ftr] = bk_facs.apply(ftr_func[ftr], axis=1)

    segs = gp.read_file(path_segs)
    matched = lns_polys2lns(bk_facs, segs, bfr_crs, bfr_func, init_crs=init_crs)
    matched = matched.merge(bk_facs, left_on=index_ln, right_index=True)
    features = []
    for index_seg, grp in matched.groupby(index_seg):
        features.append(tuple([index_seg]+[tuple(x for x in grp[c].values if (not pd.isnull(x)) and not x=='') for c in ftr_name_bk_facs]))
    features = pd.DataFrame(features,columns=[index_seg]+ftr_name_bk_facs)

    both_way = lambda x: 'both' if (x==('both',) or len(x)>1) else '' if len(x)==0 else x[0]
    features['cycle_lane'] = features['cycle_lane'].apply(both_way)
    features['cycle_way'] = features['cycle_way'].apply(both_way)
    features['side_walk'] = features['side_walk'].apply(both_way)
    features['bikable'] = features['bikable'].apply(lambda x: 'yes' if 'yes' in x else '' if len(x)==0 else 'no' )
    features['is_shared'] = features['is_shared'].apply(lambda x: 1 if len(x)>0 else 0)

    features.to_csv(path_ftr_bk_facs, encoding='utf-8')
    if debug:
        print '# bk facs in osm =', bk_facs.shape[0]
        print '# bk facs by features:'
        for f in ftr_name_bk_facs:
            print f, zip(bk_facs[f].value_counts().index, bk_facs[f].value_counts().values)
        print '# matches between bk facs and segs =', matched.shape[0]
        for f in ftr_name_bk_facs:
            print f, zip(features[f].value_counts().index, features[f].value_counts().values)
    return features