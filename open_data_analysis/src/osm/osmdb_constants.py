# coding=utf-8
TB_GEOM = 'geometry'
TB_MMBR = 'member'
TB_TAG = 'tag'

FIELDS_TB_GEOM = ['ot', 'oid', 'wkb']
FIELDS_TB_GEOM_LOADED = ['ot', 'oid', 'geometry']
FIELDS_TB_TAG = ['ot', 'oid', 'key', 'value']

tag_highway = [('highway', None)]
tag_admin_have = [('boundary', None), ('place', None)]
tag_admin_donthave = [('leisure', None), ('amenity', None), ('boundary', ['national_park', 'protected_area']),
                      ('natural', None), ('place', ['island', 'islet', 'square', 'farm'])]
tag_restriction = [('restriction', None), ('restriction:conditional', None), ('restriction:hgv', None)]
tag_landuse = [('landuse', None)]
tag_bk_facs = [
    ('highway', ['path', 'pedestrian', 'footway', 'cycleway', 'crossing', 'track']),
    ('cycleway', None),
    ('cycleway:left', None),
    ('cycleway:right', None),
    ('cycleway:both', None),
    ('oneway:bicycle', None),
    ('bicycle', None),
    ('bicycle:lanes', None),
    ('bicycle:backward', None),
    ('amenity', ['bicycle_parking', 'bicycle_rental']),
    ('foot', None),
    ('sidewalk', None),
    ('segregated', None)
]
