# coding=utf-8
import geopandas as gp


def frsq_near_segments(frsq_venues_in_city_path, city_segments_path, bfr_crs, bfr_func, init_crs=4326, store=True):
    """
    filter FourSquare venues near segments based on bfr_func.
    If store, frsq_near_segments with be stored as file {venues_path}_near_{segs_path}.geojson
    """
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

