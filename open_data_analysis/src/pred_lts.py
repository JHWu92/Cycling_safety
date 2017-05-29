# coding=utf-8
from ftr_aggregate import load_joint_features
from sk_ml import fillna
from constants import dir_data, fn_target_lts_dc
import pandas as pd
from sklearn.model_selection import train_test_split


def prepare_lts_dataset(scaler, fna=0.0, years=(2014, 2015, 2016, 2017), total_or_not='total', return_type='list'):
    assert return_type in ('list', 'dict'), 'allowed return type: "list" or "dict"'

    print 'loading feature and fill NAN'
    ftr, col2code = load_joint_features(years=years, how=total_or_not)
    ftr_name = list(ftr.columns)
    ftr = fillna(ftr, how=fna)

    print 'loading LTS and remove 10'
    lts = pd.read_csv(dir_data + fn_target_lts_dc, index_col=0)
    lts = lts[lts.LTS != 10].dropna()

    print 'creating train and test set'
    dataset = lts.merge(ftr, left_index=True, right_index=True)
    train, test = train_test_split(dataset, test_size=0.2, random_state=0)
    train_y = train.LTS
    train_x = train.drop('LTS', axis=1)
    test_y = test.LTS
    test_x = test.drop('LTS', axis=1)

    print 'normalizing X'
    scaler.fit(train_x)
    train_x = scaler.transform(train_x)
    test_x = scaler.transform(test_x)
    if return_type == 'list':
        return train_x, train_y, test_x, test_y, ftr_name, col2code
    elif return_type == 'dict':
        return {'train_x' : train_x, 'train_y': train_y, 'test_x': test_x, 'test_y': test_y,
                'ftr_name': ftr_name, 'col2code': col2code}
    else:
        return None
