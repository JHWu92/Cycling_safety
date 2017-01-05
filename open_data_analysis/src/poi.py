# coding=utf-8
import geopandas as gp
import pandas as pd


def mapping_for_fs(path_mapping_for_fs):
    result = []
    with open(path_mapping_for_fs) as f:
        lvs = ['','','','','','','','','']
        for line in f:
            line = line.split('\t')
            lv = len(line)
            node = line[-1].strip()
            lvs[lv]=node
            parent = '/'.join(lvs[:lv])
            result.append([lv, node, parent, lvs[1]])
    new_taxonomy = pd.DataFrame(result,columns=['lv','tag','parents','top_parent'])
    return pd.Series(new_taxonomy.top_parent.values,index=new_taxonomy.tag).to_dict()


def map_frsq_venues_to_poi_category(frsq_venues_gpdf, path_mapping_for_fs, debug=False):
    print '===========mapping  frsq venues to poi categories==========='
    mapping = mapping_for_fs(path_mapping_for_fs)
    poi_frsq = frsq_venues_gpdf.copy()
    poi_frsq['mapped'] = poi_frsq.category.apply(lambda x: mapping[x.encode('utf-8')] if x.encode('utf-8') in mapping else 'no category')

    if debug:
        unmapped = poi_frsq[poi_frsq.mapped=='no category']
        print 'venues without poi category: #venues={}, #frsq_categories={}'.format(len(unmapped), len(pd.unique(unmapped.category)))
        print 'top ten frsq_categories', unmapped.category.value_counts().order(ascending=False).head(10).to_dict()

    poi_frsq = poi_frsq[['id','name','mapped','geometry']]
    poi_frsq.columns = ['id','name','category','geometry']
    return poi_frsq


def mapping_for_osm(path_mapping_for_osm):
    result = []
    with open(path_mapping_for_osm) as f:
        category, key, value = '','',''
        for line in f:
            line_ = line
            line = line.split('\t')
            type_ = len(line)
            txt = line[-1].strip()
            if type_==1:
                category = txt
            elif type_==2:
                key = txt
            elif type_==3:
                value = txt
                result.append([category, key, value])
    new_taxonomy = pd.DataFrame(result,columns=['category', 'key', 'value'])
    mapping = pd.Series(new_taxonomy.category.values,
              index=new_taxonomy.apply(lambda x: '{}={}'.format(x.key, x.value), axis=1).values
             ).to_dict()
    return mapping


def map_osm_to_poi_category(path_osm_db, path_mapping_for_osm, debug=True):
    print '===========mapping osm to poi category==========='
    from osm.osmdb_filter import filter_tbtag, filter_geom_by_otoids_to_gpdf
    from osm.osmdb_constants import FIELDS_TB_TAG
    from constants import var_exclude_category_for_osm
    assert FIELDS_TB_TAG==['ot', 'oid', 'key', 'value'], 'Assume fields of table tag are ot,oid,key,value'

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

    poi_osm = pd.DataFrame(mapped, columns=FIELDS_TB_TAG[:2]+['category'])
    poi_osm = poi_osm[poi_osm.category!=var_exclude_category_for_osm].groupby(['ot','oid']).agg(set).reset_index()
    shapes = filter_geom_by_otoids_to_gpdf(path_osm_db, poi_osm[['ot','oid']].values.tolist())
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
    rs = poi_osm[poi_osm.ot=='R']
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
    assert len(rs_else)==0, 'unexpected geometry type in rltn'
    rs_pt = gp.GeoDataFrame(rs_pt, columns=['ot','oid','geometry','category'])
    rs_ln_pl = gp.GeoDataFrame(rs_ln_pl, columns=['ot','oid','geometry','category'])
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
    nds = poi_osm[poi_osm.ot=='N']
    wys = poi_osm[poi_osm.ot=='W']
    pts = merge_with_rltn(nds, rs_pt)
    ln_pls = merge_with_rltn(wys, rs_ln_pl)
    return pts, ln_pls


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
