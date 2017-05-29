# coding: utf-8

import os

from src.pred_lts import prepare_lts_dataset
from src.sk_ml import scaler_by_name, sk_models, grid_cv_default_params, grid_cv_models, evaluate_grid_cv, \
    evaluator_scalable_cls

if __name__ == '__main__':
    fna = 0.0
    years = (2014, 2015, 2016, 2017)
    total_or_not = 'TOTAL'
    scaler_type = 'MinMaxScaler'

    cv_dir = 'data/cross_validation/na_{}-year_{}-total_{}-norm_{}'.format(fna, years, total_or_not, scaler_type)
    if not os.path.exists(cv_dir):
        os.mkdir(cv_dir)

    scaler = scaler_by_name(scaler_type)
    train_x, train_y, test_x, test_y = prepare_lts_dataset(scaler, fna, years, total_or_not)

    print 'get models and grid_cv tuning parameters'
    models = sk_models(stoplist=())
    params = grid_cv_default_params()

    # run grid cv and save result
    df_cv_res = grid_cv_models(train_x, train_y, models, params, path=cv_dir, verbose=True)

    # evaluate best model of each kind and save result
    df_eval = evaluate_grid_cv(df_cv_res, train_x, train_y, test_x, test_y, evaluator_scalable_cls, path=cv_dir)
