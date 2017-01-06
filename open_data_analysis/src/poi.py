# coding=utf-8
import geopandas as gp
import pandas as pd
import numpy as np


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
        print 'venues without poi category: #venues={}, #frsq_categories={}'.format(len(unmapped),
                                                                                    len(pd.unique(unmapped.category)))
        print 'top ten frsq_categories', unmapped.category.value_counts().order(ascending=False).head(10).to_dict()

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


def remove_osm_frsq_overlap(poi_osm_pts, poi_frsq, path_osm_db, bfr_crs, init_crs=4326, bfr_range=5, debug=True):
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
    return poi_pts


def poi_distribution(poi_frsq, poi_osm, poi):
    poi_frsq_distr = poi_frsq.category.value_counts().reset_index()
    poi_frsq_distr.columns = ['category','fs']

    categories, counts = np.unique(np.hstack(poi_osm.category.apply(list).apply(np.array).values), return_counts=True)
    poi_osm_distr = pd.DataFrame(zip(categories,counts),columns=['category','osm'])

    categories, counts = np.unique(np.hstack(poi.category.apply(list).apply(np.array).values), return_counts=True)
    poi_distr = pd.DataFrame(zip(categories,counts),columns=['category','poi'])
    return poi_frsq_distr.merge(poi_osm_distr).merge(poi_distr)


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
