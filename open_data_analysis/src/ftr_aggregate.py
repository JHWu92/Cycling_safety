import geopandas as gp
import pandas as pd
import numpy as np
from src.constants import fn_features_dc, dir_data, index_seg, features_for_total

def load_joint_features(years=(2014,2015,2016,2017), how='NO_TOTAL', verbose=False):
    """
    for each feature files: get dummies, dummy_na=True; fillna with 0; encode each feature names with ftr_name_No
    return joint features and code book
    """
    features = load_separate_features(verbose=verbose)
    joint_features = []
    ftr_code2desc = {}
    for name, df in features.items():
        ftr = df.copy()
        ftr = filter_year(ftr, years=years)
        if name in features_for_total:
            ftr = filter_total(ftr, name, how=how)
        ftr,mapping = encode_col(ftr, name)
        ftr = ftr.groupby(level=0).sum()

        joint_features.append(ftr)
        ftr_code2desc.update(mapping)

    joint_features = reduce(lambda x, y: pd.merge(x, y, left_index=True, right_index=True, how='outer'), joint_features)
    
    return joint_features, ftr_code2desc


def load_separate_features(verbose=True):
    """
    get dummies, dummy_na=True
    fillna with 0
    """
    features = {}
    for name, fn in fn_features_dc.items():
        if verbose:  print 'loading feature:', fn
        df = pd.read_csv(dir_data + fn, index_col=0)
        if index_seg in df.columns:
            df.set_index('index_seg', inplace=True)
        df = pd.get_dummies(df, dummy_na=True)
        df.fillna(0, inplace=True)
        features[name] = df
    return features


def filter_year(ftr, years=(2014, 2015, 2016, 2017), keep_year=False):
    if 'YEAR' in ftr.columns:
        ftr = ftr[ftr.YEAR.isin(years)]
        if not keep_year:
            ftr = ftr[ftr.columns[~ftr.columns.isin(['YEAR', 'MONTH'])]]
    return ftr


def filter_total(ftr, name, how='NO_TOTAL'):
    assert how in ('NO_TOTAL', 'TOTAL'), 'only allow two options: NO_TOTAL and TOTAL'
    if how=='NO_TOTAL':
        new_columns = [c for c in ftr.columns if 'total' not in c]
    else:
        new_columns = [c for c in ftr.columns if 'total' in c]
        if not new_columns:
            ftr[name + '_total'] = ftr.sum(axis=1)
            new_columns = [name + '_total']
    if 'YEAR' in ftr.columns and 'YEAR' not in new_columns:
        new_columns = ['YEAR','MONTH']+new_columns
    return ftr[new_columns]


def encode_col(ftr, name):
    """
    This encode_col will affect the passing df, make sure you copy it before passing.
    """
    num_col = ftr.shape[1]
    new_col = ['{}_{:03d}'.format(name, i) for i in range(num_col)]
    mapping = dict(zip(new_col, ftr.columns))
    ftr.columns = new_col
    return ftr, mapping




