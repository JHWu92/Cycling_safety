# coding=utf-8
import sqlite3
from osmdb_constants import TB_GEOM, TB_MMBR, TB_TAG

def build_db_from_osm(osm_container, city, osm_db_path):
    """
    Given osm raw data, create sqlite db with osm_clean
    :param osm_container: osm raw data loaded by osm.container.OSMContainer
    :param city: city polygon in shapely.geometry.Polygon
    :param osm_db_path: path of the db file
    :return: None
    """
    from osm_clean import oid_in_city, duplicate_osm
    print 'running osm_clean'
    oic = oid_in_city(osm_container, city)
    keep_oids, merge_oids, one_node_ways = duplicate_osm(osm_container,oic)
    print 'finished osm_clean'

    print 'begin building db'
    create_tb_idx(osm_db_path)
    insert_geom(osm_container, osm_db_path, keep_oids)
    insert_tag(osm_container, osm_db_path, keep_oids, merge_oids)
    insert_mmbr(osm_container, osm_db_path, keep_oids)
    print 'built db'


def create_connection(osm_db_path):
    """ create a database connection to the SQLite database
        specified by osm_db_path
    :param osm_db_path: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(osm_db_path)
        return conn
    except Exception as e:
        print(e)

    return None


def create_tb_idx(osm_db_path):

    sql_ct_geom = '''
    CREATE TABLE IF NOT EXISTS {tb} (
     ot text NOT NULL,
     oid integer NOT NULL,
     wkb VARBINARY NOT NULL,
     CONSTRAINT pk_geom_otoid PRIMARY KEY (ot, oid)
    );
    '''.format(tb=TB_GEOM)

    sql_ct_mmbr = '''
    CREATE TABLE IF NOT EXISTS {tb} (
     rid integer NOT NULL,
     mot text,
     moid integer,
     role text
    );
    '''.format(tb=TB_MMBR)

    sql_ct_tag = '''
    BEGIN;
    CREATE TABLE IF NOT EXISTS {tb} (
     ot text NOT NULL,
     oid integer NOT NULL,
     key text,
     value text,
     UNIQUE (ot, oid, key, value)
    );
    CREATE INDEX IF NOT EXISTS {tb}_ot_oid_idx ON {tb} (ot, oid);
    CREATE INDEX IF NOT EXISTS {tb}_key_idx ON {tb} (key);
    COMMIT;
    '''.format(tb=TB_TAG)

    with create_connection(osm_db_path) as conn:
        c = conn.cursor()
        c.execute(sql_ct_geom)
        c.execute(sql_ct_mmbr)
        c.executescript(sql_ct_tag)
        conn.commit()


def insert_geom(osm_container,osm_db_path, keep_oids):

    from osm2shp import node2pt, way2lineOrpoly, rltn2geocltn
    values = []
    for otype in ['Node','Way','Relation']:
        ot = otype[0]
        keep = keep_oids[otype]
        o2s = {'Node': node2pt, 'Way': way2lineOrpoly, 'Relation': rltn2geocltn}[otype]
        for obj in osm_container.osm_objs[otype]:
            if not obj.id in keep:
                continue
            shp = o2s(obj) if otype=='Node' else o2s(osm_container, obj)
            values.append((ot,obj.id, shp.wkb))

    with create_connection(osm_db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany('INSERT INTO {tb} (ot, oid, wkb) VALUES (?,?,?)'.format(tb=TB_GEOM), values)
        print 'inserted {} row(s) to TABLE {}'.format(cursor.rowcount, TB_GEOM)


def insert_tag(osm_container, osm_db_path, keep_oids, merge_oids):
    values = []
    for otype in ['Node','Way', 'Relation']:
        ot = otype[0]
        keep = keep_oids[otype]
        merge = merge_oids[otype]
        for obj in osm_container.osm_objs[otype]:
            oid = obj.id
            if not oid in keep:
                continue
            tags = obj.tags.items()
            if oid in merge:
                for be_merged_oid in merge[oid]:
                    be_merged_obj = osm_container.get_osm_obj_by_id(otype,be_merged_oid)
                    tags.extend(be_merged_obj.tags.items())
            tags = list(set(tags))
            tags = [(ot, oid, key, value) for key, value in tags]
            values.extend(tags)

    with create_connection(osm_db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany('INSERT INTO {tb} (ot, oid, key, value) VALUES (?,?,?,?)'.format(tb=TB_TAG), values)
        print 'inserted {} row(s) to TABLE {}'.format(cursor.rowcount,TB_TAG)


def insert_mmbr(osm_container, osm_db_path, keep_oids):
    from osmread import Node, Way, Relation
    ot2str = {Node:'N', Way:'W', Relation:'R'}
    values = []
    for rltn in osm_container.osm_objs['Relation']:
        if rltn.id not in keep_oids['Relation']:
            continue
        for m in rltn.members:
            values.append((rltn.id, ot2str[m.type], m.member_id, m.role))

    with create_connection(osm_db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany('INSERT INTO {tb} (rid, mot, moid, role) VALUES (?,?,?,?)'.format(tb=TB_MMBR), values)
        print 'inserted {} row(s) to TABLE {}'.format(cursor.rowcount, TB_MMBR)

