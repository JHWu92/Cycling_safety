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


def frsq_near_segments(frsq_venues_in_city_path, city_segments_path, bfr_crs, bfr_func, init_crs=4326, store=False):
    """
    filter FourSquare venues near segments based on bfr_func.
    If store, frsq_near_segments with be stored as file {venues_path}_near_{segs_path}.geojson
    """
    print '=====filtering frsq near segments====='
    from geom_helper import objs_near_segs
    import os

    frsq_venues_in_city = gp.read_file(frsq_venues_in_city_path)
    city_segments = gp.read_file(city_segments_path)
    frsq_venues_near_segments = objs_near_segs(frsq_venues_in_city, city_segments, bfr_func, bfr_crs, output='objs', init_crs=init_crs)
    print '# venues in city=',frsq_venues_in_city.shape[0]
    print '# venues near segments=', frsq_venues_near_segments.shape[0]

    if store:
        fn_venues, ext = os.path.splitext(frsq_venues_in_city_path)
        fn_segs, ext = os.path.splitext(os.path.basename(city_segments_path))
        new_path = '{fnv}_near_{fns}{ext}'.format(fnv=fn_venues, fns=fn_segs, ext=ext)
        with open(new_path, 'w') as f:
            f.write(frsq_venues_near_segments.to_json())
        print 'wrote frsq_near_segments:', new_path

    return frsq_venues_near_segments

