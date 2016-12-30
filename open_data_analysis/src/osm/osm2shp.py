
import shapely.geometry as shpgeo
from shapely.ops import linemerge
from osmread import Node, Way, Relation

# import sys, os
# dir_path = os.path.dirname(os.path.realpath(__file__))
# par_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
# sys.path.insert(0, par_dir_path)
# from geo_helper import remove_equal_shpobj, merge_within_by_list_shp


def node2pt(node):
    return shpgeo.Point(node.lon, node.lat)


def way2line(osm_container, way):
    nodes = [osm_container.get_osm_node_by_id(nid) for nid in way.nodes]
    return shpgeo.LineString([(node.lon, node.lat) for node in nodes])


def lon_lats_closed(lon_lats):
    return lon_lats[0] == lon_lats[-1]


def way2lineOrpoly(osm_container, way):
    import warnings
    nodes = [osm_container.get_osm_node_by_id(nid) for nid in way.nodes]
    lon_lats = [(node.lon, node.lat) for node in nodes]
    obj = shpgeo.Polygon(lon_lats) if lon_lats_closed(lon_lats) and len(lon_lats) > 3 else shpgeo.LineString(lon_lats)
    if not obj.is_valid:
        warnings.warn("way id={} is not valid as a {}".format(way.id, type(obj)))
        obj = obj.buffer(0)
    return obj


def rltn2shps(osm_container, relation, sub_rltn=False, to='dict'):
    allow_to = {'dict','list'}
    if to not in allow_to:
        raise ValueError('allow to = {dict, list}')
    nodes, ways, sub_nodes, sub_ways = [], [], [], []
    for m in relation.members:
        obj = osm_container.get_osm_obj_by_id(m.type, m.member_id)
        if m.type == Node:
            nodes.append(obj)
        elif m.type == Way:
            ways.append(obj)
        elif m.type == Relation:
            r_nodes, r_ways = rltn2shps(osm_container, obj, sub_rltn=True)
            sub_nodes.extend(r_nodes)
            sub_ways.extend(r_ways)
    nodes.extend([node for node in sub_nodes])
    ways.extend([way for way in sub_ways])

    if sub_rltn:
        return nodes, ways

    points = [node2pt(node) for node in nodes]
    lines = [way2line(osm_container, way) for way in ways]

    dict_shp= {'Point': points, 'LineString': [], 'Polygon': []}
    if lines:
        merged = linemerge(lines)
        if merged.type == 'LineString':
            merged = [merged]
        else:
            merged = list(merged)
        for ln in merged:
            if ln.is_ring:
                dict_shp['Polygon'].append(shpgeo.Polygon(ln))
            else:
                dict_shp['LineString'].append(ln)
    if to=='dict':
        return dict_shp
    elif to=='list':
        return dict_shp['Point'] + dict_shp['LineString'] + dict_shp['Polygon']


def rltn2geocltn(osm_container, rltn):
    from shapely.geometry.collection import GeometryCollection
    return GeometryCollection(rltn2shps(osm_container, rltn, to='list'))