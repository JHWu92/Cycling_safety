def costs(start_time):
    import datetime
    dnow = datetime.datetime.now()
    delta = dnow - start_time
    del_secs = int(delta.total_seconds())
    return 'now = %s, costs = %d days %02d:%02d:%02d' % (dnow.strftime('%Y-%m-%d %H:%M:%S'), del_secs / 3600 / 24,
                                                         del_secs / 3600 % 24, del_secs / 60 % 60, del_secs % 60)


def file_name_without_extension(fn):
    import os
    return os.path.splitext(fn)[0]


def make_sure_path_exists(path_or_fn):
    import os
    import errno
    try:
        os.makedirs(path_or_fn)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def group_consecutive(data, stepsize=1):
    """
    group consecutive number as as sub list.
    E.g. data = [1, 2, 3, 5, 6, 7, 10, 11]
    stepsize=1: return [[1,2,3], [5,6,7], [10,11]]
            =2: return [[1,2,3,5,6,7], [10,11]]
    :param data: list/array
    :param stepsize: define consecutive.
    """
    import numpy as np
    return np.split(data, np.where(np.diff(data) > stepsize)[0] + 1)


def even_chunks(array, max_chunk_size, indices=False, right_close=False):
    import math
    size = len(array)
    num_chunks = math.ceil(size * 1.0 / max_chunk_size)
    new_chunk_size = int(math.ceil(size * 1.0 / num_chunks))
    return get_chunks(array, new_chunk_size, indices, right_close=right_close)


def get_chunks(array, chunk_size, indices=False, right_close=False):
    """Yield successive chunks with chunk_size from array.
    params:
        indices: if false, yield chunks of array; if True, yield indices pair (left, right) only
        right_close: if False return elements with indices in [left, right); if True, return indices in [left, right]
    """
    for i in range(0, len(array), chunk_size):
        left = i
        right = min(len(array), i + chunk_size + right_close)
        if indices:
            yield (left, right)
        else:
            yield array[left: right]


# =============================================
# basic type variable
# =============================================
def is_str(s):
    return isinstance(s, str) or isinstance(s, unicode)


def float_round(num, places=1, direction='up'):
    from math import ceil, floor
    assert direction in ['up', 'down'], 'direction options are: up and down'
    func = {'up': ceil, 'down': floor}[direction]
    return func(num * (10 ** places)) / float(10 ** places)


# =============================================
# time manipulation
# =============================================
def strptime(str_time, form='%Y-%m-%dT%H:%M:%SZ'):
    from datetime import datetime as dt
    return dt.strptime(str_time, form)


def strftime(time, form='%Y-%m-%dT%H:%M:%SZ'):
    from datetime import datetime as dt
    return dt.strftime(time, format=form)


def diff_in_sec(minuend, subtrahend, form='%Y-%m-%dT%H:%M:%SZ'):
    if is_str(minuend):
        minuend = strptime(minuend, form)
    if is_str(subtrahend):
        subtrahend = strptime(subtrahend, form)
    return (minuend - subtrahend).total_seconds()


def add_secs(time, secs, form='%Y-%m-%dT%H:%M:%SZ', return_str=True):
    import datetime
    if is_str(time):
        time = strptime(time)
    new_time = time + datetime.timedelta(seconds=secs)
    new_time = strftime(new_time) if return_str else new_time
    return new_time