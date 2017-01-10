# coding=utf-8
import geopandas as gp
import pandas as pd
import numpy as np
from constants import index_seg, index_obj


def get_feature_poi(path_frsq, path_osm_db, path_segs, path_mapping_frsq, path_mapping_osm, path_poi_distr, path_feature_poi, path_cvrg, path_box, segs_bfr_func, pts_bfr_range, bfr_crs, init_crs=4326, debug=False):
    """
    1. mapped frsq venues to poi categories --> filter frsq venues by obj_near_segment
    2. mapped osm data to poi categories, filter osm data by obj_near_segment
    3. remove overlap between osm and frsq
    4. Visalization:
        - poi categories distribution
            1. frsq venues near segments
            2. osm venues near segments
            3. final poi near segments(after removing overlap)
        - poi categories per segment distribution
    :return seg_poi_features, poi_distr, poi_near_segs, seg_poi_index
    """
    from utils import change_ext
    from geom_helper import objs_near_segs
    # map frsq to poi
    frsq_venues = gp.read_file(path_frsq)
    poi_frsq = map_frsq_venues_to_poi_category(frsq_venues, path_mapping_frsq, debug=debug)
    # map osm to poi and split osm into points and line/polygon
    poi_osm = map_osm_to_poi_category(path_osm_db, path_mapping_osm, debug=debug)
    poi_osm_pts, poi_osm_ln_pls = clean_and_split_poi_osm_by_geometry(poi_osm)
    # remove overlap between osm points and FourSquare Venues, get buffered frsq and osm points
    poi_pts, poi_frsq_bfr, poi_osm_pts_bfr = remove_osm_frsq_overlap(poi_osm_pts, poi_frsq, path_osm_db, bfr_crs, init_crs=init_crs, bfr_range=pts_bfr_range, debug=debug)
    poi_osm_bfr = poi_osm_pts_bfr.append(poi_osm_ln_pls, ignore_index=True)
    # append points and line/polygon
    poi = poi_osm_ln_pls.append(poi_pts, ignore_index=True)
    # keep poi nearby segments
    segs = gp.read_file(path_segs)
    poi_frsq_near_segs = objs_near_segs(poi_frsq_bfr, segs, segs_bfr_func, bfr_crs, output='objs')
    poi_osm_near_segs = objs_near_segs(poi_osm_bfr, segs, segs_bfr_func, bfr_crs, output='objs')
    seg_poi_index, poi_near_segs = objs_near_segs(poi, segs, segs_bfr_func, bfr_crs, output='index_and_objs')
    if debug:
        print '# venues in city =',poi_frsq.shape[0]
        print '# osm after clean in city, # points = {}, # line/polygon = {}'.format(poi_osm_pts.shape[0], poi_osm_ln_pls.shape[0])
        print '# poi in dc = {}, # poi near seg dc = {}'.format(poi.shape[0], poi_near_segs.shape[0])
        print '# objs have category near seg by ot:', poi_near_segs.ot.value_counts().to_dict()

    poi_distr = poi_distribution(poi_frsq_near_segs, poi_osm_near_segs, poi_near_segs)
    poi_distr.to_csv(path_poi_distr, encoding='utf-8')
    path_plot_poi_distr = change_ext(path_poi_distr, '.html')
    plot_poi_distribution(poi_distr, ipynb=False, path=path_plot_poi_distr)
    seg_poi_features = poi_per_seg_distribution(seg_poi_index, poi_near_segs)
    segs_cnt = segs.shape[0]
    print '# segs with poi: {}/{}={}%'.format(len(seg_poi_features), segs_cnt, len(seg_poi_features)*100.0/segs_cnt)
    seg_poi_features.to_csv(path_feature_poi, encoding='utf-8')
    plot_poi_per_seg(seg_poi_features, segs_cnt, ipynb=False, path_cvrg=path_cvrg, path_box=path_box)
    return seg_poi_features, poi_distr, poi_near_segs, seg_poi_index


def mapping_for_fs(path_mapping_for_fs):
    result = []
    with open(path_mapping_for_fs) as f:
        lvs = ['', '', '', '', '', '', '', '', '']
        for line in f:
            line = line.split('\t')
            lv = len(line)
            node = line[-1].strip()
            lvs[lv] = node
            parent = '/'.join(lvs[:lv])
            result.append([lv, node, parent, lvs[1]])
    new_taxonomy = pd.DataFrame(result, columns=['lv', 'tag', 'parents', 'top_parent'])
    return pd.Series(new_taxonomy.top_parent.values, index=new_taxonomy.tag).to_dict()


def map_frsq_venues_to_poi_category(frsq_venues_gpdf, path_mapping_for_fs, debug=False):
    print '===========mapping  frsq venues to poi categories==========='
    mapping = mapping_for_fs(path_mapping_for_fs)
    poi_frsq = frsq_venues_gpdf.copy()
    poi_frsq['mapped'] = poi_frsq.category.apply(
        lambda x: mapping[x.encode('utf-8')] if x.encode('utf-8') in mapping else 'no category')

    if debug:
        unmapped = poi_frsq[poi_frsq.mapped == 'no category']
        print '# venues with poi =', len(poi_frsq) - len(unmapped)
        print 'venues without poi category: #venues={}, #frsq_categories={}'.format(len(unmapped), len(pd.unique(unmapped.category)))
        print 'top ten unmapped frsq_categories', unmapped.category.value_counts().order(ascending=False).head(10).to_dict()

    poi_frsq = poi_frsq[['id', 'name', 'mapped', 'geometry']]
    poi_frsq.columns = ['id', 'name', 'category', 'geometry']
    return poi_frsq


def mapping_for_osm(path_mapping_for_osm):
    result = []
    with open(path_mapping_for_osm) as f:
        category, key, value = '', '', ''
        for line in f:
            line_ = line
            line = line.split('\t')
            type_ = len(line)
            txt = line[-1].strip()
            if type_ == 1:
                category = txt
            elif type_ == 2:
                key = txt
            elif type_ == 3:
                value = txt
                result.append([category, key, value])
    new_taxonomy = pd.DataFrame(result, columns=['category', 'key', 'value'])
    mapping = pd.Series(new_taxonomy.category.values,
                        index=new_taxonomy.apply(lambda x: '{}={}'.format(x.key, x.value), axis=1).values
                        ).to_dict()
    return mapping


def map_osm_to_poi_category(path_osm_db, path_mapping_for_osm, debug=True):
    print '===========mapping osm to poi category==========='
    from osm.osmdb_filter import filter_tbtag, filter_geom_by_otoids_to_gpdf
    from osm.osmdb_constants import FIELDS_TB_TAG
    from constants import var_exclude_category_for_osm
    assert FIELDS_TB_TAG == ['ot', 'oid', 'key', 'value'], 'Assume fields of table tag are ot,oid,key,value'

    rows = filter_tbtag(path_osm_db)

    mapping = mapping_for_osm(path_mapping_for_osm)
    mapped = []
    for ot, oid, key, value in rows:
        key_value = '{}={}'.format(key.encode('utf-8'), value.encode('utf-8'))
        key_ = key + '=*'
        category = ''
        if key_value in mapping:
            category = mapping[key_value]
        elif key_ in mapping:
            category = mapping[key_]
        if category:
            mapped.append((ot, oid, category))

    poi_osm = pd.DataFrame(mapped, columns=FIELDS_TB_TAG[:2] + ['category'])
    poi_osm = poi_osm[poi_osm.category != var_exclude_category_for_osm].groupby(['ot', 'oid']).agg(set).reset_index()
    shapes = filter_geom_by_otoids_to_gpdf(path_osm_db, poi_osm[['ot', 'oid']].values.tolist())
    poi_osm = shapes.merge(poi_osm)

    if debug:
        print '# rows in table tag  =', len(rows)
        print '# rows after mapping =', len(mapped)
        print '# objs have category =', len(poi_osm)
        print '# objs have category by ot:', poi_osm.ot.value_counts().to_dict()
        print '# categories: # objs =', poi_osm.category.apply(len).value_counts().to_dict()

    return poi_osm


def break_down_rltns(poi_osm):
    from shapely.geometry import Point, LineString, Polygon
    rs = poi_osm[poi_osm.ot == 'R']
    rs_pt, rs_ln_pl, rs_else = [], [], []
    for _, r in rs.iterrows():
        geom = r.geometry
        for x in geom:
            rs_list = []
            if isinstance(x, LineString) or isinstance(x, Polygon):
                rs_list = rs_ln_pl
            elif isinstance(x, Point):
                rs_list = rs_pt
            else:
                rs_list = rs_else
            rs_list.append((r.ot, r.oid, x, r.category))
    assert len(rs_else) == 0, 'unexpected geometry type in rltn'
    rs_pt = gp.GeoDataFrame(rs_pt, columns=['ot', 'oid', 'geometry', 'category'])
    rs_ln_pl = gp.GeoDataFrame(rs_ln_pl, columns=['ot', 'oid', 'geometry', 'category'])
    return rs_pt, rs_ln_pl


def merge_with_rltn(n_or_w, rs):
    # TODO: assigning rltn tag to equal ln may not be a good idea. mainly related to members with role "inner"
    # TODO: how to keep role information of rltn's geometrycollection --> either osmdb_create.py or osm2shp.py
    # TODO: examples see developing poi.ipynb
    from geom_helper import gpdf_equal
    equal_idx = gpdf_equal(n_or_w, rs)
    for index_left, index_right in equal_idx.values:
        n_or_w.loc[index_left].category |= rs.loc[index_right].category
    rs_indp = rs[~rs.index.isin(equal_idx.index_right)]
    return n_or_w.append(rs_indp, ignore_index=True)


def clean_and_split_poi_osm_by_geometry(poi_osm):
    """ This function alters category column of some rows in poi_osm
    """
    rs_pt, rs_ln_pl = break_down_rltns(poi_osm)
    nds = poi_osm[poi_osm.ot == 'N']
    wys = poi_osm[poi_osm.ot == 'W']
    pts = merge_with_rltn(nds, rs_pt)
    ln_pls = merge_with_rltn(wys, rs_ln_pl)
    return pts, ln_pls


def similar_name(row, threshold):
    return row.name_sml > threshold


def no_name_but_same_category(row, no_name_value):
    if not row.name_sml == no_name_value:
        return False
    assert isinstance(row.category_right, set) and isinstance(row.category_left, set), 'type of category is not set'
    return len(row.category_right - row.category_left) == 0


def remove_osm_frsq_overlap(poi_osm_pts, poi_frsq, path_osm_db, bfr_crs, init_crs=4326, bfr_range=5, debug=False):
    print '=====remove_osm_frsq_overlap====='
    from geom_helper import crs_prepossess
    from osm.osmdb_filter import filter_tbtag_to_df
    from utils import similarity
    from geom_helper import connected_nodes
    from constants import similar_name_threshold, no_name_value
    from shapely.ops import cascaded_union

    # data preprossesing: bfr osm and frsq, join names for osm
    osm_bfr = crs_prepossess(poi_osm_pts, init_crs, bfr_crs)
    osm_bfr.geometry = osm_bfr.buffer(bfr_range)
    osm_bfr = osm_bfr.to_crs(epsg=init_crs)

    frsq_bfr = crs_prepossess(poi_frsq, init_crs, bfr_crs)
    frsq_bfr.geometry = frsq_bfr.buffer(bfr_range)
    frsq_bfr = frsq_bfr.to_crs(epsg=init_crs)
    frsq_bfr.category = frsq_bfr.category.apply(lambda x: set([x]))

    osm_with_name = filter_tbtag_to_df(path_osm_db, in_tags=[('name', None)])

    osm_bfr_name = osm_bfr.merge(osm_with_name, how='left')
    osm_bfr_name.drop('key', axis=1, inplace=True)
    osm_bfr_name.columns = list(osm_bfr.columns) + ['name']
    osm_bfr_name.name = osm_bfr_name.name.fillna('')

    # find overlap: spatial join, calculate name similarity for each row in sjoin
    # compute connected component, find overlap by name similarity or same category within each component
    sjoin = gp.tools.sjoin(osm_bfr_name, frsq_bfr).reset_index()
    sjoin['name_sml'] = sjoin.apply(lambda x: similarity(x.name_left, x.name_right), axis=1)

    pairs = sjoin[['oid', 'id']].values
    conn_nodes = connected_nodes(pairs)
    if debug:
        print '# conn components(osm_pts connected with frsq): ', len(conn_nodes)

    mask_component = lambda df, x: df[(df.oid.isin(x)) | df['id'].isin(x)]
    over_lap_dfs = []
    for conn_idx, pts_idxes in enumerate(conn_nodes):
        pts_idxes = set(pts_idxes)
        mask = mask_component(sjoin, pts_idxes)
        assert set(mask[['oid', 'id']].values.flatten()) == pts_idxes, (conn_idx, pts_idxes, mask)
        mask_name_sml = mask[mask.apply(lambda x: similar_name(x, similar_name_threshold), axis=1)].copy()
        if mask_name_sml.shape[0] > 0:
            mask_name_sml['criteria'] = 'similar name'
            mask_name_sml['component_idx'] = conn_idx
            over_lap_dfs.append(mask_name_sml)
        else:
            mask_same_cateory = mask[mask.apply(lambda x: no_name_but_same_category(x, no_name_value), axis=1)].copy()
            mask_same_cateory['criteria'] = 'same category'
            mask_same_cateory['component_idx'] = conn_idx
            over_lap_dfs.append(mask_same_cateory)

            # merge overlap, append independent points and overlap
    overlaps = pd.concat(over_lap_dfs)
    overlap_oid = np.unique(overlaps.oid)
    overlap_fqid = np.unique(overlaps['id'])
    osm_indp = osm_bfr_name[~osm_bfr_name.oid.isin(overlap_oid)]
    frsq_indp = frsq_bfr[~frsq_bfr['id'].isin(overlap_fqid)]

    overlap_merged = []
    for idx, row in overlaps.iterrows():
        oid, fqid = row.oid, row['id']
        category = row.category_left | row.category_right
        pts = [row.geometry]
        pts.append(frsq_bfr[frsq_bfr['id'] == fqid].geometry.values[0])
        union_pts = cascaded_union(pts)
        ot = row.ot + '_fq'
        overlap_merged.append((ot, oid, category, union_pts))
    overlap_merged = gp.GeoDataFrame(overlap_merged, columns=['ot', 'oid', 'category', 'geometry'])

    poi_pts = pd.concat([osm_indp, frsq_indp, overlap_merged], ignore_index=True)

    if debug:
        print '# pairs of overlap', overlaps.shape
        print '# pairs by overlap criteria', overlaps.criteria.value_counts().to_dict()
        print 'distribution of # pairs of overlap within each connected component', overlaps.component_idx.value_counts().value_counts().to_dict()
        print '# overlap points in osm = {}, # points in fs = {}'.format(overlap_oid.shape[0], overlap_fqid.shape[0])
        print '# independent points in osm = {}, # points in fs = {}'.format(osm_indp.shape[0], frsq_indp.shape[0])
        print '# total points in osm = {}, # points in fs = {}'.format(osm_bfr.shape[0], frsq_bfr.shape[0])
        # indp osm unique id + overlap osm unique id != total points, because
        # a) rltn could have multiple pts, b) one node can have multiple name because osm has duplicate data
    return poi_pts, frsq_bfr, osm_bfr


def get_sum_categories(list_mapped):
    from collections import defaultdict
    sum_categories = defaultdict(int)
    for mapped in list_mapped:
        for c in list(mapped):
            sum_categories[c]+=1
    return sum_categories


def poi_distribution(poi_frsq, poi_osm, poi):
    poi_frsq_distr = pd.DataFrame(get_sum_categories(poi_frsq.category.values).items())
    poi_frsq_distr.columns = ['category','fs']

    poi_osm_distr = pd.DataFrame(get_sum_categories(poi_osm.category.values).items())
    poi_osm_distr.columns = ['category','osm']

    poi_distr = pd.DataFrame(get_sum_categories(poi.category.values).items())
    poi_distr.columns = ['category','poi']

    return poi_frsq_distr.merge(poi_osm_distr).merge(poi_distr)


def poi_per_seg_distribution(seg_poi_index, poi_near_seg):
    from constants import poi_categories
    seg_poi_index_category = seg_poi_index.merge(poi_near_seg[['category']], left_on=index_obj, right_index=True)
    poi_per_seg = {}
    for idx, grp in seg_poi_index_category.groupby(index_seg):
        poi_per_seg[idx] = dict(get_sum_categories(grp.category.values))
    poi_per_seg = pd.DataFrame(poi_per_seg.items(),columns=[index_seg,'category'])
    for l in poi_categories:
        poi_per_seg[l] = poi_per_seg.category.apply(lambda x: x.get(l,0) if type(x)!=float else 0)
    poi_per_seg['total'] = poi_per_seg[poi_categories].sum(axis=1)
    poi_per_seg.drop('category',axis=1,inplace=True)
    return poi_per_seg


def plot_poi_distribution(poi_distr, percentage='both', ipynb=False, path=None):
    if percentage=='both':
        print 'plot poi distribution'
        from utils import add_suffix
        plot_poi_distribution(poi_distr, percentage='no', ipynb=ipynb, path=path)
        if path:
            path = add_suffix(path, '_pcnt')
        plot_poi_distribution(poi_distr, percentage='yes', ipynb=ipynb, path=path)
        return
    else:
        if ipynb:
            from plotly.offline import iplot as pplot, init_notebook_mode
            init_notebook_mode()
        else:
            assert path, 'variable path could not be null'
            from plotly.offline import plot as pplot
        import plotly.graph_objs as pgo
        from constants import poi_categories

        fs = poi_distr.fs
        osm = poi_distr.osm
        poi = poi_distr.poi
        if percentage=='yes':
            fs = fs/fs.sum()
            osm = osm/osm.sum()
            poi = poi/poi.sum()
        data = [
            pgo.Bar(x=poi_categories, y=poi, name='poi'),
            pgo.Bar(x=poi_categories, y=osm, name='osm'),
            pgo.Bar(x=poi_categories, y=fs, name='foursquare'),
        ]
        layout = pgo.Layout(title='POI distribution',xaxis=dict(title='category'), yaxis=dict(title='# poi'))
        fig = pgo.Figure(data=data, layout=layout)
        pplot(fig, filename=path)


def plot_poi_per_seg(poi_per_seg, cnt_segs, ipynb=False, path_cvrg=None, path_box=None):
    print 'plot poi per seg'
    if ipynb:
        from plotly.offline import iplot as pplot, init_notebook_mode
        init_notebook_mode()
    else:
        assert path_cvrg and path_box, 'variable path could not be null'
        from plotly.offline import plot as pplot
    import plotly.graph_objs as pgo
    from constants import poi_categories
    labels = ['total']+poi_categories

    coverage_per_category = [poi_per_seg[poi_per_seg[label]!=0].shape[0]*1.0/cnt_segs for label in labels]
    data = [pgo.Bar(y=coverage_per_category, x = labels)]
    layout = pgo.Layout(title='POI coverage', xaxis=dict(title='category'), yaxis=dict(title='# seg with poi / # segs'))
    fig = pgo.Figure(data=data, layout=layout)
    pplot(fig, filename=path_cvrg)

    data = [pgo.Box(y=poi_per_seg[label],name=label) for label in labels]
    layout = pgo.Layout(title='POI boxplot per category', xaxis=dict(title='category'), yaxis=dict(title='# poi per seg'))
    fig = pgo.Figure(data=data, layout=layout)
    pplot(fig, filename=path_box)


# def frsq_near_segments(frsq_venues_in_city_path, city_segments_path, bfr_crs, bfr_func, init_crs=4326, store=False):
#     """
#     filter FourSquare venues near segments based on bfr_func.
#     If store, frsq_near_segments with be stored as file {venues_path}_near_{segs_path}.geojson
#     """
#     print '=====filtering frsq near segments====='
#     from geom_helper import objs_near_segs
#     import os
#
#     frsq_venues_in_city = gp.read_file(frsq_venues_in_city_path)
#     city_segments = gp.read_file(city_segments_path)
#     frsq_venues_near_segments = objs_near_segs(frsq_venues_in_city, city_segments, bfr_func, bfr_crs, output='objs', init_crs=init_crs)
#     print '# venues in city=',frsq_venues_in_city.shape[0]
#     print '# venues near segments=', frsq_venues_near_segments.shape[0]
#
#     if store:
#         fn_venues, ext = os.path.splitext(frsq_venues_in_city_path)
#         fn_segs, ext = os.path.splitext(os.path.basename(city_segments_path))
#         new_path = '{fnv}_near_{fns}{ext}'.format(fnv=fn_venues, fns=fn_segs, ext=ext)
#         with open(new_path, 'w') as f:
#             f.write(frsq_venues_near_segments.to_json())
#         print 'wrote frsq_near_segments:', new_path
#
#     return frsq_venues_near_segments
#
