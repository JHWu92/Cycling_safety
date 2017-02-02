# coding=utf-8


def make_type_consistent(s1, s2):
    """If both objects aren't either both string or unicode instances force them to unicode"""
    if isinstance(s1, str) and isinstance(s2, str): return s1, s2
    elif isinstance(s1, unicode) and isinstance(s2, unicode): return s1, s2
    else: return unicode(s1), unicode(s2)


def similarity(a,b):
    import difflib
    from constants import no_name_value
    if len(a)==0 or len(b)==0:
        return no_name_value
    a,b = make_type_consistent(a,b)
    a,b = a.lower(), b.lower()
    match_size = sum([m.size for m in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_matching_blocks()])*1.0
    longer_size, shorter_size = (len(b),len(a)) if len(a)<len(b) else ((len(a),len(b)))
    longer_size = shorter_size if (longer_size/1.5)<=shorter_size else longer_size/1.5
#     return match_size/(longer_size+shorter_size)*2
    return match_size/shorter_size


def change_ext(fn, new_ext):
    import os
    base = os.path.splitext(fn)[0]
    if not new_ext.startswith('.'):
        new_ext = '.' + new_ext
    return base + new_ext


def add_suffix(fn, suf):
    import os
    base, ext = os.path.splitext(fn)
    return base + suf + ext


def costs(start_time):
    import datetime
    dnow = datetime.datetime.now()
    delta = dnow - start_time
    delta_total_seconds_int = int(delta.total_seconds())
    return 'now = %s, costs = %d days %02d:%02d:%02d = %d seconds' % (dnow.strftime('%Y-%m-%d %H:%M:%S'),
                                                                      delta_total_seconds_int / 3600 / 24,
                                                                      delta_total_seconds_int / 3600 % 24,
                                                                      delta_total_seconds_int / 60 % 60,
                                                                      delta_total_seconds_int % 60,
                                                                      delta_total_seconds_int)
