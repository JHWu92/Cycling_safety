# coding=utf-8
import geopandas as gp
from shapely.geometry import Point, LineString, Polygon


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


def grid_area(w, s, e, n, ngrid=10):
    """
    grid area into ngrid^2 grids
    :param w, s, e, n,: the w, s, e, n (min_lon, min_lat, max_lon, max_lat) of the bound box
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
            grids.append((wj, si, ej, ni))
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
    if gpdf_crs.crs == None:
        gpdf_crs.crs = {'init': u'epsg:{}'.format(init_crs)}
    return gpdf_crs.to_crs(epsg=bfr_crs)


# ###### buffer function for objs_near_segs ######
def bfr_20m(seg):
    return seg.geometry.buffer(20)


def objs_near_segs(objs, segs, bfr_func, bfr_crs, init_crs=4326, output='seg_obj_index', crs_ready=False):
    """
    obj indexes of whom are near segments
    :param objs: geopandas.GeoDataFrame
    :param segs: geopandas.GeoDataFrame
    :param bfr_func: define "near"
    :param init_crs: init_crs epsg code
    :param bfr_crs: target crs epsg code used for buffering
    :param output: one kind of ('seg_obj_index', 'objs')
    :return: geopandas.GeoDataFrame objs[near segs]
    """
    allow_output = ('seg_obj_index', 'objs')
    if output not in allow_output:
        raise ValueError('output should be one of (seg_obj_index, objs)')
    seg_crs = segs.copy() if crs_ready else crs_prepossess(segs, init_crs, bfr_crs)
    obj_crs = objs if crs_ready else crs_prepossess(objs, init_crs, bfr_crs)
    seg_crs.geometry = seg_crs.apply(bfr_func, axis=1)

    sjoin = gp.tools.sjoin(seg_crs, obj_crs, how='left', op='intersects')
    if output == 'seg_obj_index':
        seg_obj_index = sjoin['index_right'].reset_index()
        seg_obj_index.columns = ['seg_index', 'obj_index']
        return seg_obj_index
    elif output == 'objs':
        obj_idx_nearby = set(sjoin[~sjoin.index_right.isnull()].index_right)
        objs_nearby = objs[objs.index.isin(obj_idx_nearby)]
        return objs_nearby


def objs_near_segs_store(objs_near, path_objs, path_segs):
    import os
    dir_fn_objs, ext = os.path.splitext(path_objs)
    fn_segs, ext = os.path.splitext(os.path.basename(path_segs))
    new_path = '{}_near_{}{}'.format(dir_fn_objs, fn_segs, ext)
    with open(new_path, 'w') as f:
        f.write(objs_near.to_json())
    print 'wrote obj near segments:', new_path


# ########## functions assigning ln(segment) to objs #############
def pts2lns(pts, lns, bfr_crs, init_crs=4326, close_jn_dist=5, far_jn_dist=20):
    """
    1. close jn: buffer pts in bfr_crs with close_jn_dist, use sjoin to find segment(s) intersected with buffered pts
    2. far jn: for pts without any segment in close jn, buffer them with far_jn_dist and find nearest segment
    :param pts: geopandas.GeoDataFrame
    :param lns: geopandas.GeoDataFrame
    :param bfr_crs: target crs epsg code used for buffering
    :param init_crs: init_crs epsg code, default 4326(lat lon)
    :param close_jn_dist: close join distance, allowing multiple segments for one point(assumed as intersection)
    :param far_jn_dist: far join distance, find the nearest segment for one point
    :return: pandas.DataFrame, columns=[pt_index, ln_index]
    """

    import pandas as pd

    lns_crs = crs_prepossess(lns, init_crs, bfr_crs)
    pts_crs = crs_prepossess(pts, init_crs, bfr_crs)

    close_jn = pts_crs.copy()
    close_jn.geometry = close_jn.buffer(close_jn_dist)
    close_jn = gp.tools.sjoin(close_jn, lns_crs)[['index_right']]

    close_jn_pts = set(pd.unique(close_jn.index))
    far_jn = pts_crs[~pts_crs.index.isin(close_jn_pts)].copy()
    far_jn.geometry = far_jn.buffer(far_jn_dist)
    far_jn = gp.tools.sjoin(far_jn, lns_crs)[['index_right']]
    # calculate haversine distance
    far_jn = pd.merge(lns[['geometry']], far_jn, left_index=True, right_on=['index_right'])
    far_jn = pd.merge(pts[['geometry']], far_jn, left_index=True, right_index=True)
    far_jn['dis'] = far_jn.apply(lambda x: ptfromln(x.geometry_x, x.geometry_y), axis=1)
    # keep ln with minimum distance to pt
    far_jn = far_jn.groupby(level=0).apply(lambda x: x.iloc[x.dis.values.argmin()][['index_right']])

    pts_has_ln = close_jn.append(far_jn).reset_index()
    pts_has_ln.columns = ['pt_index', 'ln_index']

    pts_no_ln = pts[~pts.index.isin(pd.unique(pts_has_ln.pt_index))].copy()
    return pts_has_ln, pts_no_ln


def lns_polys2lns(lns_polys, segs, bfr_crs, bfr_func, init_crs=4326, cvr_thres=0.3, sum_thres=0.8):
    # keep polys' exteriors
    lns = lns_polys.copy()
    lns.geometry = lns.geometry.apply(lambda x: x.exterior if isinstance(x, Polygon) else x)

    # prepare crs and bfr
    lns_crs = crs_prepossess(lns, init_crs, bfr_crs)
    segs_crs = crs_prepossess(segs, init_crs, bfr_crs)
    segs_bfr = segs_crs.copy()
    segs_bfr.geometry = segs_bfr.apply(bfr_func, axis=1)

    # get candidate seg-ln pairs
    sjoin = gp.tools.sjoin(segs_bfr, lns_crs, how='left', op='intersects')
    sjoin = sjoin.reset_index()[['index', 'index_right', 'geometry']]
    sjoin.columns = ['index_seg', 'index_ln', 'geometry_seg_bfr']
    sjoin = sjoin.merge(lns_crs[['geometry']], left_on='index_ln', right_index=True)
    sjoin = sjoin.merge(segs_crs[['geometry']], left_on='index_seg', right_index=True)
    sjoin.columns = list(sjoin.columns[:3]) + ['geometry_ln', 'geometry_seg']

    # compute coverage of ln over seg
    sjoin['cvr'] = sjoin.apply(len_cvr, axis=1)

    # filter by cvr_thres and sum_thres
    sum_len = sjoin[sjoin.cvr > cvr_thres][['index_seg', 'cvr']].groupby('index_seg').agg(sum)
    seg_indexes = set(sum_len[sum_len.cvr > sum_thres].index)

    return sjoin[(sjoin.index_seg.isin(seg_indexes)) & (sjoin.cvr > cvr_thres)][['index_seg', 'index_ln', 'cvr']]


def dot(va, vb):
    return va[0] * vb[0] + va[1] * vb[1]


def ang(lna, lnb):
    import math
    # Get nicer vector form
    va = [(lna[0][0] - lna[1][0]), (lna[0][1] - lna[1][1])]
    vb = [(lnb[0][0] - lnb[1][0]), (lnb[0][1] - lnb[1][1])]
    # Get dot prod
    dot_prod = dot(va, vb)
    # Get magnitudes
    maga = dot(va, va) ** 0.5
    magb = dot(vb, vb) ** 0.5
    if maga == 0 or magb == 0:
        return 0
    # Get cosine value
    cos_ = dot_prod / maga / magb
    cos_ = cos_ if cos_ < 1 else 1
    cos_ = cos_ if cos_ > -1 else -1
    # Get angle in radians and then convert to degrees
    angle = math.acos(cos_)
    ang_deg = math.degrees(angle) % 360

    if ang_deg - 180 >= 0:
        ang_deg = 360 - ang_deg
    if ang_deg > 90:
        return 180 - ang_deg
    return ang_deg


def filter_lns_by_angle(ln, seg, ang_thres=10):
    pts = [Point(pt) for pt in ln.coords]
    projs = [seg.project(pt) for pt in pts]
    proj_ln = LineString([seg.interpolate(pt) for pt in projs])
    ln_coords = ln.coords
    proj_ln_coords = proj_ln.coords
    sublns = zip(ln_coords[:-1], ln_coords[1:])
    subprojlns = zip(proj_ln_coords[:-1], proj_ln_coords[1:])
    keep_pts = []
    keep_ln_len = 0.0
    for i in range(len(sublns)):
        if LineString(subprojlns[i]).length != 0 and ang(sublns[i], subprojlns[i]) < ang_thres:
            keep_pts.extend(sublns[i])
            keep_ln_len += LineString(sublns[i]).length
    return keep_pts, keep_ln_len


def len_cvr(row, ang_thres=10):
    seg = row.geometry_seg
    seg_length = seg.length
    seg_bfr = row.geometry_seg_bfr
    ln = row.geometry_ln
    intersected_ln = ln.intersection(seg_bfr)
    if isinstance(intersected_ln, Point):
        return 0
    if isinstance(intersected_ln, LineString):
        intersected_ln = [intersected_ln]
    proj_positions = []
    intersected_ln_len = 0
    for subln in intersected_ln:
        if isinstance(subln, Point):
            continue
        keep_pts, keep_ln_len = filter_lns_by_angle(subln, seg, ang_thres)
        proj_positions.extend([seg.project(Point(pt_coords)) for pt_coords in keep_pts])
        intersected_ln_len += keep_ln_len
    if len(proj_positions) == 0:
        return 0
    cover_len = max(proj_positions) - min(proj_positions)
    cover_len = cover_len if cover_len < intersected_ln_len else intersected_ln_len
    #     return intersected_ln
    return cover_len / seg_length

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
