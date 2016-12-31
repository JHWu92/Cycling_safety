# coding=utf-8

# #############
# functions based on lon lat tuple
# ##########


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    from math import radians, cos, sin, asin, sqrt
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    m = km * 1000
    return m


def grid_line(mini, maxi, ngrid=10):
    delta = (maxi - mini) / ngrid
    return [(mini + i * delta, mini + (i + 1) * delta) for i in range(ngrid)]


def grid_area(s, w, n, e, ngrid=10):
    """
    grid area into ngrid^2 grids
    :param s, w, n, e: the s,w,n,e lat lon points of the bound box
    :param ngrid: divide area into ngrid^2 grids
    :return: list of grid represented by bound box with s,w,n,e
    """
    grid_lat = grid_line(s, n, ngrid)
    grid_lon = grid_line(w, e, ngrid)
    grids = []
    for i in range(ngrid):
        for j in range(ngrid):
            si, ni = grid_lat[i]
            wj, ej = grid_lon[j]
            grids.append((si, wj, ni, ej))
    return grids


# ##############
# function based on shapely
# ##############


def ptfromln(pt, ln):
    """
    project pt to ln, compute haversine distance between projected pt and pt
    :param pt: shapely.geometry.Point, (lon, lat) point
    :param ln: shapely.geometry.LineString, [(lon,lat)] points
    :return: distance in meters
    """
    n_pt = ln.interpolate(ln.project(pt))
    lon1, lat1 = n_pt.coords[0]
    lon2, lat2 = pt.coords[0]
    return haversine(lon1, lat1, lon2, lat2)


# ##############
# function based on geopandas
# ##############


def crs_prepossess(gpdf, init_crs, bfr_crs):
    """
    create a shallow copy of gpdf; check the init crs of gpdf, if None, assign init_crs; change crs of copy to bfr_crs
    :param gpdf: geopandas.GeoDataFrame
    :param init_crs: init_crs epsg code
    :param bfr_crs: target crs epsg code used for buffering
    :return: a shallow copy of gpdf in bfr_crs
    """
    gpdf_crs = gpdf.copy()
    if gpdf_crs.crs==None:
        gpdf_crs.crs = {'init': u'epsg:{}'.format(init_crs)}
    return gpdf_crs.to_crs(epsg=bfr_crs)


# ###### buffer function for objs_near_segs ######
def bfr_20m(seg):
    return seg.geometry.buffer(20)


def objs_near_segs(objs, segments, bfr_func, init_crs, bfr_crs):
    """
    keep objs that are near segments
    :param objs: geopandas.GeoDataFrame
    :param segments: geopandas.GeoDataFrame
    :param bfr_func: define "near"
    :param init_crs: init_crs epsg code
    :param bfr_crs: target crs epsg code used for buffering
    :return: geopandas.GeoDataFrame objs[near segs]
    """
    import geopandas as gp
    seg_crs = crs_prepossess(segments, init_crs, bfr_crs)
    obj_crs = crs_prepossess(objs, init_crs, bfr_crs)
    seg_crs.geometry = seg_crs.apply(bfr_func,axis=1)

    sjoin = gp.tools.sjoin(seg_crs, obj_crs, how='left',op='intersects')
    obj_ids_nearby = set(sjoin[~sjoin.index_right.isnull()].index_right)
    objs_nearby = objs[objs.index.isin(obj_ids_nearby)]
    return objs_nearby


# ########## functions assigning segment to objs #############
def pts2seg(pts, segs, bfr_crs, init_crs=4326, close_jn_dist=5, far_jn_dist=20):
    """
    1. close jn: buffer pts in bfr_crs with close_jn_dist, use sjoin to find segment(s) intersected with buffered pts
    2. far jn: for pts without any segment in close jn, buffer them with far_jn_dist and find nearest segment
    :param pts: geopandas.GeoDataFrame
    :param segs: geopandas.GeoDataFrame
    :param bfr_crs: target crs epsg code used for buffering
    :param init_crs: init_crs epsg code, default 4326(lat lon)
    :param close_jn_dist: close join distance, allowing multiple segments for one point(assumed as intersection)
    :param far_jn_dist: far join distance, find the nearest segment for one point
    :return: pandas.DataFrame, columns=[pt_index, seg_index]
    """

    import geopandas as gp
    import pandas as pd

    seg_crs = crs_prepossess(segs, init_crs, bfr_crs)
    pts_crs = crs_prepossess(pts, init_crs, bfr_crs)

    close_jn = pts_crs.copy()
    close_jn.geometry = close_jn.buffer(close_jn_dist)
    close_jn = gp.tools.sjoin(close_jn, seg_crs)[['index_right']]

    close_jn_pts = set(pd.unique(close_jn.index))
    far_jn = pts_crs[~pts_crs.index.isin(close_jn_pts)].copy()
    far_jn.geometry = far_jn.buffer(far_jn_dist)
    far_jn = gp.tools.sjoin(far_jn, seg_crs)[['index_right']]
    # calculate haversine distance
    far_jn = pd.merge(segs[['geometry']], far_jn, left_index=True, right_on=['index_right'])
    far_jn = pd.merge(pts[['geometry']], far_jn, left_index=True, right_index=True)
    far_jn['dis']=far_jn.apply(lambda x: ptfromln(x.geometry_x, x.geometry_y),axis=1)
    # keep seg with minimum distance to pt
    far_jn = far_jn.groupby(level=0).apply(lambda x: x.iloc[x.dis.values.argmin()][['index_right']])

    pts_has_seg = close_jn.append(far_jn).reset_index()
    pts_has_seg.columns=['pt_index', 'seg_index']

    pts_no_seg = pts[~pts.index.isin(pd.unique(pts_has_seg.pt_index))].copy()
    return pts_has_seg, pts_no_seg


def ln_poly2seg():
    return

# ==================
# old version
# ===================

# every pts would have a seg, by buffering gradually
# def pts2seg(gp_pts, gp_segs, init_crs=4326, bfr_crs=3559, near_dis_thres=5, buffer_dis=50):
#     """
#     pts and segs are assumed as geopandas.GeoDataFrame with crs:4326, which means (lon,lat) points
#     1. check crs and change crs to epsg:3559 (NAD83(NSRS2007) / Maryland)
#     2. get segid of near seg(s) based on var:near_dis_thres for each point
#     3. for those points without any near segs
#      - buffer them var:buffer_dis meters to find near segs
#      - use func:ptfromln to get on earth distance from point to line
#      - get one segid of the nearest seg
#     """
#     import geopandas as gp
#     import pandas as pd
#
#
#     gp_pts_crs = crs_prepossess(gp_pts,init_crs,bfr_crs)
#     gp_segs_crs = crs_prepossess(gp_segs,init_crs,bfr_crs)
#
#     gp_pts_crs_bfr = gp_pts_crs.copy()
#     gp_pts_crs_bfr.geometry = gp_pts_crs_bfr.buffer(near_dis_thres)
#
#     close_jn = gp.tools.sjoin(gp_pts_crs_bfr, gp_segs_crs)[['index_right']]
#
#     processed_pts = set(pd.unique(close_jn.index))
#     mask = (~gp_pts_crs_bfr.index.isin(processed_pts))
#     far_jns = []
#     while gp_pts_crs_bfr[mask].shape[0]!=0:
#         gp_pts_crs_bfr.loc[mask, 'geometry'] = gp_pts_crs_bfr[mask].buffer(buffer_dis)
#         jn = gp.tools.sjoin(gp_pts_crs_bfr[mask], gp_segs_crs)[['index_right']]
#         far_jns.append(jn)
#         processed_pts |= set(pd.unique(jn.index))
#         mask = (~gp_pts_crs_bfr.index.isin(processed_pts))
#
#     far_jns = pd.concat(far_jns)
#     mr_far_jns = pd.merge(gp_segs[['geometry']],far_jns , left_index=True, right_on=['index_right'])
#     mr_far_jns = pd.merge(gp_pts[['geometry']],mr_far_jns, left_index=True, right_index=True)
#     mr_far_jns['dis']=mr_far_jns.apply(lambda x: ptfromln(x.geometry_x, x.geometry_y),axis=1)
#
#     group = mr_far_jns.groupby(level=0).apply(lambda x: x.iloc[x.dis.values.argmin()][['index_right']])
#     result = close_jn.append(group).reset_index()
#     result.columns=['pt_index', 'seg_index']
#     return result
#
