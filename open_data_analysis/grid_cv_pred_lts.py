# coding: utf-8

import os

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from src.constants import fn_target_lts_dc, dir_data
from src.ftr_aggregate import load_joint_features
from src.sk_ml import *

if __name__ == '__main__':
    fna = 0.0
    years = (2014, 2015, 2016, 2017)
    total = 'NO_TOTAL'
    normalization = 'MinMaxScaler'

    cv_dir = 'data/cross_validation/na_{}-year_{}-total_{}-norm_{}'.format(fna, years, total, normalization)

    if not os.path.exists(cv_dir):
        os.mkdir(cv_dir)

    print 'load feature and fill NAN'
    ftr, mapping = load_joint_features(years=years, how=total)
    ftr = fillna(ftr, how=fna)

    print 'load LTS and remove 10'
    lts = pd.read_csv(dir_data + fn_target_lts_dc, index_col=0)
    lts = lts[lts.LTS!=10].dropna()

    print 'create train and test set'
    dataset = lts.merge(ftr, left_index=True, right_index=True)
    train, test = train_test_split(dataset, test_size=0.2, random_state=0)
    train_y = train.LTS
    train_x = train.drop('LTS', axis=1)
    test_y = test.LTS
    test_x = test.drop('LTS', axis=1)

    print 'normalize X'
    scaler = MinMaxScaler().fit(train_x)
    train_x = scaler.transform(train_x)
    test_x = scaler.transform(test_x)

    print 'get models and grid_cv tuning parameters'
    models = sk_models(stoplist=())
    params = grid_cv_default_params()

    # run grid cv and save result
    df_cv_res = grid_cv_models(train_x, train_y, models, params, path=cv_dir, verbose=True)

    # evaluate best model of each kind and save result
    df_eval = evaluate_grid_cv(df_cv_res, train_x, train_y, test_x, test_y, evaluator_scalable_cls, path=cv_dir)
