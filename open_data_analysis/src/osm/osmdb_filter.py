# coding=utf-8
from osmdb_constants import TB_TAG, TB_GEOM


def exec_sql(osm_db, sql, text_factory_str=False):
    import sqlite3
    with sqlite3.connect(osm_db) as conn:
        if text_factory_str:
            conn.text_factory = str
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
    return rows


def get_geom_by_otoid(osm_db, ot, oid):
    """
    :return: shapley.geometry of ot, oid
    """
    from shapely.wkb import loads as load_wkb_str
    sql = "SELECT * FROM {tb} WHERE ot='{ot}' AND oid={oid}".format(tb=TB_GEOM, ot=ot, oid=oid)
    rows = exec_sql(osm_db, sql, text_factory_str=True)
    assert len(rows) <= 1, 'fetch data by ot={} oid={} with more than one row'.format(ot, oid)
    if len(rows) == 1:
        return load_wkb_str(rows[0][2])
    print 'no geometry match ot={}, oid={} in db: {}'.format(ot, oid, osm_db)
    return None


def chunk(l, size=400):
    for i in range(0, len(l), size):
        yield l[i:i+size]


def filter_table_by_otoids(osm_db, otoids, table, debug=False, text_factory_str=False):
    """
    :return: rows of table geometry
    """
    assert otoids, 'otoids should not be empty'
    assert is_list_tuple(otoids[0]), 'elements of otoids should be list or tuple: otoids={}'.format(str(otoids))
    rows = []
    for sub_otoids in chunk(otoids):
        pair_clause = []
        for cnt, (ot, oid) in enumerate(sub_otoids):
            if cnt==0:
                pair_clause.append("SELECT '{}' AS ot, {} AS oid".format(ot, oid))
            else:
                pair_clause.append("SELECT '{}', {}".format(ot, oid))
        pair_clause = ' UNION ALL '.join(pair_clause)
        sql = 'SELECT * FROM {}'.format(table)
        sql = '{sql} NATURAL JOIN ({pair_clause})'.format(sql=sql, pair_clause=pair_clause)
        if debug:
            print sql
        rows.extend(exec_sql(osm_db, sql,text_factory_str))
    return rows


def filter_geom_by_otoids(osm_db, otoids, debug=False):
    """
    :return: rows of table geometry
    """
    rows = filter_table_by_otoids(osm_db, otoids, TB_GEOM, debug=debug, text_factory_str=True)
    return rows


def filter_geom_by_otoids_to_gpdf(osm_db, otoids, debug=False):
    import geopandas as gp
    from shapely.wkb import loads as load_wkb_str
    from osmdb_constants import FIELDS_TB_GEOM_LOADED
    rows = filter_geom_by_otoids(osm_db, otoids, debug)
    gpdf = gp.GeoDataFrame(rows, columns=FIELDS_TB_GEOM_LOADED)
    gpdf.geometry = gpdf.geometry.apply(lambda x: load_wkb_str(x))
    return gpdf


def is_list_tuple(obj):
    return isinstance(obj, list) or isinstance(obj, tuple)


def build_clause(tags):
    clause = []
    for key, value in tags:
        if key:
            if not value:  # tag:some_k=*
                clause.append("key='{}'".format(key))
            elif not is_list_tuple(value):  # tag:some_k=some_v
                clause.append("key='{}' and value='{}'".format(key, value))
            else:
                v_clause = ' or '.join(["value='{}'".format(v) for v in value])
                clause.append("key='{}' and ({})".format(key, v_clause))
    return clause


def filter_tag_by_otoids(osm_db, otoids, debug=False):
    rows = filter_table_by_otoids(osm_db, otoids, TB_TAG, debug=debug)
    return rows


def filter_tbtag_to_df(osm_db, in_tags=((None, None),), ex_tags=((None, None),), ot=None, debug=False):
    from osmdb_constants import FIELDS_TB_TAG
    import pandas as pd
    rows = filter_tbtag(osm_db, in_tags, ex_tags, ot, debug)
    return pd.DataFrame(rows, columns=FIELDS_TB_TAG)


def filter_tbtag(osm_db, in_tags=((None, None),), ex_tags=((None, None),), ot=None, debug=False, distinct_otoid=False):
    """
    filter table tag where row has ot, one of the tag in in_tags and none of the ex_tags
    :param osm_db: osm db file path
    :param in_tags: INcluding one of these TAGS, list of (key, value) pairs
    :param ex_tags: EXcluding all of these TAGS, list of (key, value) pairs
    :param ot: short form osm type [N for Node, W for Way, R for Relation]
    :param debug: if True, print sql and basic statistics of rows
    :return: rows fitting where clause
    """
    from osmdb_constants import FIELDS_TB_TAG
    assert FIELDS_TB_TAG==['ot', 'oid', 'key', 'value'], 'filter_tbtag assumes fields of table tag are ot,oid,key,value'
    sql = "SELECT * FROM {tb}".format(tb=TB_TAG)  # tag=(*,*), any objs with any tag
    if distinct_otoid:
        sql = "SELECT distinct ot, oid FROM {tb}".format(tb=TB_TAG)
    assert is_list_tuple(in_tags[0]), 'elements of in_tags should be tuple or list, tags={}'.format(in_tags)
    assert is_list_tuple(ex_tags[0]), 'elements of ex_tags should be tuple or list, tags={}'.format(ex_tags)
    in_tags_clause = build_clause(in_tags)
    ex_tags_clause = build_clause(ex_tags)

    where_clause = []

    if ot:
        where_clause.append("ot='{}'".format(ot))
    if in_tags_clause:
        where_clause.append('(' + ') or ('.join(in_tags_clause) + ')')
    if ex_tags_clause:
        where_clause.append('not((' + ') or ('.join(ex_tags_clause) + '))')

    where_clause = ') AND ('.join(where_clause)

    sql = '{sql} WHERE ({where})'.format(sql=sql, where=where_clause) if where_clause else sql
    if debug:
        print 'filter table tag:', sql

    rows = exec_sql(osm_db, sql)

    if debug:
        import pandas as pd
        if distinct_otoid:
            df = pd.DataFrame(rows, columns=FIELDS_TB_TAG[:2])
            print '# rows', len(rows)
            print 'ot:', pd.unique(df.ot)
        else:
            df = pd.DataFrame(rows, columns=FIELDS_TB_TAG)
            print '# rows', len(rows)
            print 'ot:', pd.unique(df.ot)
            print '# keys', len(pd.unique(df.key))
            if len(pd.unique(df.key)) < 5:
                print 'keys:', pd.unique(df.key)
                for key in pd.unique(df.key):
                    print 'key =', key, 'value:', pd.unique(df[df.key == key].value)
        print '==========================='
        print

    return rows


def select_bk_facs(osm_db, ot=None, debug=False, df=False):
    from osmdb_constants import tag_bk_facs, FIELDS_TB_TAG
    otoids = filter_tbtag(osm_db, ot=ot, in_tags=tag_bk_facs, debug=debug, distinct_otoid=True)
    rows = filter_tag_by_otoids(osm_db, otoids)
    if df:
        import pandas as pd
        rows = pd.DataFrame(rows, columns=FIELDS_TB_TAG)
    return rows


# def get_objs_by_