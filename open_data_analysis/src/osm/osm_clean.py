# coding=utf-8
from osmread import Node, Way, Relation


def get_city(city_path):
    import geopandas as gp
    city = gp.read_file(city_path).geometry.values[0]
    return city


def oid_in_city(osm_container, city):
    """
    osm raw data is downloaded in bound box. Find osm objs within the given city polygon
    :param osm_container: osm raw data loaded by osm.container.OSMContainer
    :param city: city polygon in shapely.geometry.Polygon
    :return: {'Node':node_ids, 'Way': way_ids, 'Relation': rltn_ids}
    """
    from osm2shp import node2pt, rltn2shps
    nodes = osm_container.osm_objs['Node']
    ways = osm_container.osm_objs['Way']
    rltns = osm_container.osm_objs['Relation']

    node_ids = set([node.id for node in nodes if node2pt(node).intersects(city)])
    way_ids = set([way.id for way in ways if len(set(way.nodes)&node_ids)>0])
    rltn_ids = set()

    for rltn in osm_container.osm_objs['Relation']:
        try:
            list_shps = rltn2shps(osm_container, rltn, to='list')
        except KeyError as e:
            continue
        for shp in list_shps:
            if shp.intersects(city):
                rltn_ids.add(rltn.id)
                break
    return {'Node':node_ids, 'Way': way_ids, 'Relation': rltn_ids}


def duplicate_osm(osm_container, oic):
    """
    find duplicate osm obj: Nodes with same lat lon pair; Ways with same node list(orderless) and ways with one node;
    Relations with same members (orderless)
    :param osm_container: osm raw data loaded by src.osm.container.OSMContainer
    :param oic: Osm obj id In City, computed by :func oid_in_city
    :return: keep_oids={'Node':nids, 'Way':wids, 'Relation':rid}, merge_oids(similar with keep_oids), one_node_ways(ids)
    """
    # duplicate nodes
    seen_latlons = {}
    same_nodes = {}
    for node in osm_container.osm_objs['Node']:
        if node.id in oic['Node']:
            latlon = (node.lat, node.lon)
            if not latlon in seen_latlons:
                seen_latlons[latlon]=node.id
            else:
                same_nodes[node.id] = seen_latlons[latlon]

    # duplicate ways
    seen_nodelists = {}
    same_ways = {}
    one_node_ways = []
    for way in osm_container.osm_objs['Way']:
        if not way.id in oic['Way']:
            continue
        nodelist = [same_nodes[node] if node in same_nodes else node for node in way.nodes]
        nodelist = list(set(nodelist))  # node could be duplicated within one way
        nodelist = tuple(sorted(nodelist))  # sort nodes to find duplicates
        # not keeping one-node ways
        if len(nodelist)==1:
            one_node_ways.append(way.id)
            continue
        if not nodelist in seen_nodelists:
            seen_nodelists[nodelist] = way.id
        else:
            same_ways[way.id] = seen_nodelists[nodelist]

    # duplicate relations
    seen_mlists = {}
    same_rltns = {}
    type2list = {Node:same_nodes, Way:same_ways, Relation:same_rltns}
    for rltn in osm_container.osm_objs['Relation']:
        if not rltn.id in oic['Relation']:
            continue
        mlist = []
        for m in rltn.members:
            same_list = type2list[m.type]
            mlist.append(same_list[m.member_id] if m.member_id in same_list else m.member_id)
        mlist = tuple(sorted(mlist))
        if not mlist in seen_mlists:
            seen_mlists[mlist]=rltn.id
        else:
            same_rltns[rltn.id] = seen_mlists[mlist]

    keep_oids = {'Node':set(seen_latlons.values()),
                 'Way':set(seen_nodelists.values()),
                 'Relation':set(seen_mlists.values())}

    # tags of obj in merge_oids will be added to corresponding keep_oid
    from collections import defaultdict
    merge_oids = [defaultdict(list),defaultdict(list),defaultdict(list)]
    for same, merge in zip([same_nodes, same_ways, same_rltns], merge_oids):
        for be_merged, to_merge in same.items():
            merge[to_merge].append(be_merged)
    merge_oids = dict(zip(['Node','Way','Relation'], merge_oids))

    return keep_oids, merge_oids, one_node_ways
