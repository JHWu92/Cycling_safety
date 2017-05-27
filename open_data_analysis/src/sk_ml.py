# coding=utf-8
from datetime import datetime as dtm
import os

from sklearn import linear_model, svm, tree, ensemble, neural_network, naive_bayes
from sklearn.metrics import mean_squared_error, f1_score, accuracy_score
from sklearn.model_selection import GridSearchCV
import numpy as np
import pandas as pd


def bounded_round(arr, mini, maxi):
    arr_round = arr.round()
    arr_round[arr_round<mini] = mini
    arr_round[arr_round>maxi] = maxi
    return arr_round


def fillna(df, how='mean'):
    """df is the dataset
    """
    if how == 'mean':
        return df.fillna(df.mean())
    return df.fillna(how)


def sk_models(reg=True, cls=True, stoplist=('SVM', 'SVR', 'GDBreg', 'GDBcls')):
    """
    return sk models with names by regression and/or classification.
    default stoplist is ('SVM', 'SVR', 'GDBreg', 'GDBcls') because they are too slow
    """
    reg_models = {
        'ols': linear_model.LinearRegression(),
        'ridge': linear_model.Ridge(),
        'lasso': linear_model.Lasso(),
        'DTreg': tree.DecisionTreeRegressor(),
        'RFreg': ensemble.RandomForestRegressor(),
        'ADAreg': ensemble.AdaBoostRegressor(),
        'BAGreg': ensemble.BaggingRegressor(),
        'GDBreg': ensemble.GradientBoostingRegressor(),
        'SVR': svm.SVR(),
        'linearSVR': svm.LinearSVR(),
        'MLPreg': neural_network.MLPRegressor(),
    }

    cls_models = {
        'logistics': linear_model.LogisticRegression(),
        'DTcls': tree.DecisionTreeClassifier(),
        'RFcls': ensemble.RandomForestClassifier(),
        'ADAcls': ensemble.AdaBoostClassifier(),
        'BAGcls': ensemble.BaggingClassifier(),
        'GDBcls': ensemble.GradientBoostingClassifier(),
        'SVM': svm.SVC(),
        'linearSVM': svm.LinearSVC(),
        'MLPcls': neural_network.MLPClassifier(),
        'GNBcls': naive_bayes.GaussianNB(),
    }

    models = {}
    if reg:
        for name in stoplist: reg_models.pop(name, None)
        models['reg'] = reg_models
    if cls:
        for name in stoplist: cls_models.pop(name, None)
        models['cls'] = cls_models
    return models


# ################################################
# Grid search cross validation
# ################################################

def cv_default_params():
    # GDBreg's parameters are deliberately cut down.
    params_gdb = {'n_estimators': [10, 50, 100], 'max_features': [0.1, 0.5, 1.], 'learning_rate': np.logspace(-4, 1, 3),
                  'max_depth': [3, 10, 50]},
    params_rf = {'n_estimators': [10, 30, 50, 100, 256, 500], 'max_features': [0.1, 0.3, 0.5, 1.]}
    params_ada = {'n_estimators': [10, 30, 50, 100, 256, 500], 'learning_rate': np.logspace(-4, 1, 5)}
    params_bag = {'n_estimators': [10, 30, 50, 100, 256, 500], 'max_features': [0.4, 0.7, 1.0]}

    # SVM/SVR is way too slow
    Cs = np.logspace(-4, 2, 3)
    GAMMAs = [1e-5, 1e-3, 1e-1]

    params_svm = [
        {'kernel': ['rbf'], 'C': Cs, 'gamma': GAMMAs},
        {'kernel': ['sigmoid'], 'C': Cs, 'gamma': GAMMAs},
        {'kernel': ['poly'], 'C': Cs, 'gamma': GAMMAs, 'degree': [3]},
    ]

    params_svr = [
        {'kernel': ['rbf'], 'C': Cs, 'gamma': GAMMAs},
        {'kernel': ['sigmoid'], 'C': Cs, 'gamma': GAMMAs},
        {'kernel': ['poly'], 'C': Cs, 'gamma': GAMMAs, 'degree': [3]},
    ]

    params_reg = {
        # regression
        'ols': {},
        'ridge': {'alpha': np.logspace(0, 2, 10)},
        'lasso': {'alpha': np.logspace(0, 2, 10)},
        'DTreg': {'max_depth': [3, 5, 10, 30, 50], 'max_features': [0.1, 0.3, 0.5, 1.]},
        'RFreg': params_rf,
        'ADAreg': params_ada,
        'BAGreg': params_bag,
        'GDBreg': params_gdb,
        'SVR': params_svr,
        'linearSVR': {'C': Cs, 'loss': ['epsilon_insensitive', 'squared_epsilon_insensitive'], 'epsilon': [0, 0.1, 1]},
        'MLPreg': {'hidden_layer_sizes': [(5, 2), (20, 5), (100, 20), (100, 20, 5)],
                   'learning_rate': ['constant', 'adaptive'], 'max_iter': [10000]},
    }

    params_cls = {
        'logistics': {'C': np.logspace(-4, 2, 4), 'penalty': ['l1', 'l2']},
        'DTcls': {'max_depth': [3, 5, 10, 30, 50], 'max_features': [0.1, 0.3, 0.5, 1.],
                  'criterion': ['gini', 'entropy']},
        'RFcls': params_rf,
        'ADAcls': params_ada,
        'BAGcls': params_bag,
        'GDBcls': params_gdb,
        'SVM': params_svm,
        'linearSVM': {'C': Cs, 'loss': ['hinge', 'squared_hinge']},
        'MLPcls': {'hidden_layer_sizes': [(5, 2), (20, 5), (100, 20), (100, 20, 5)],
                   'learning_rate': ['constant', 'adaptive'], 'max_iter': [10000]},
        'GNBcls': {},
    }

    return {'cls': params_cls, 'reg': params_reg}


def grid_cv_models(x, y, models, params, path='', n_jobs=4, cv=5, save_res=True, redo=False, verbose=False):
    """
    regression model is evaluated by neg_mean_squared_error
    classification model is evaluated by f1_weighted
    iterate over models' keys, get tuning parameters based on key, if no matched paramters, that model will be skipped
    if not redo and the result exists, optimum parameters will be loaded using model.set_params(**loaded)
    :return:
        index: (kind, name);
        each line is the best parameters for that model;
        type of column "best_model" is sklearn models.
    """
    path_cv_best = os.path.join(path, 'cv_%d_best_models.csv' % cv)

    if os.path.exists(path_cv_best) and not redo:
        loaded_df_cv_res = pd.read_csv(path_cv_best, index_col=[0,1])
        best_models = []
        for (kind, name), row in loaded_df_cv_res.iterrows():
            param = eval(row.best_params)
            best_models.append(models[kind][name].set_params(**param))

        loaded_df_cv_res.best_model = best_models
        print 'loaded existing cv-ed best parameters'
        return loaded_df_cv_res

    cv_results = []
    start = dtm.now()
    for kind in ['reg', 'cls']:
        if kind not in models:
            continue
        scoring = 'neg_mean_squared_error' if kind == 'reg' else 'f1_weighted'

        for name, model in models[kind].items():
            if name not in params[kind]:
                print 'model', name, 'doesnt have params, skipping it'
                continue

            param = params[kind][name]
            sub_start = dtm.now()
            print sub_start, 'CVing: kind = {}, model = {}'.format(kind, name)
            clf = GridSearchCV(model, param, n_jobs=n_jobs, cv=cv, scoring=scoring)
            clf.fit(x, y)
            sub_end = dtm.now()

            df = pd.DataFrame(clf.cv_results_).sort_values(by='mean_test_score', ascending=False)
            test_score, train_score, fit_time = df[['mean_test_score', 'mean_train_score', 'mean_fit_time']].values[0]

            if verbose:
                print 'score: %s, best test = %.3f, train = %.3f, mean_fit_time = %f' % (
                    scoring, test_score, train_score, fit_time)
                print 'best params', clf.best_params_
                print sub_end, sub_end - sub_start
                print

            result = {
                'grid_cv_time': sub_end - sub_start,
                'score': scoring,
                'model_name': name,
                'kind': kind,
                'mean_test': test_score,
                'mean_train': train_score,
                'mean_fit_time': fit_time,
                'best_params': clf.best_params_,
                'best_model': clf.best_estimator_,
            }
            cv_results.append(result)
            if save_res:
                df.to_csv(path + 'cv_%d_model_%s.csv' % (cv, name))

    end = dtm.now()
    print 'finished CV', end, end - start

    df_cv = pd.DataFrame(cv_results).set_index(['kind', 'model_name'])
    if save_res:
        df_cv.to_csv(path_cv_best)

    return df_cv


# ################################################
# Evaluate cv-ed models on test set
# Evaluators for different prediction tasks
# ################################################

def evaluate_grid_cv(df_cv, train_x, train_y, test_x, test_y, evaluator, path='', cv=5, save_res=True):
    """
    df_cv: results from :func:: grid_cv_models()
    evaluator: such as :func:: evaluator_scalable_cls()
    save_res: True->save to path/cv_%d_best_models_evaluation.csv % cv
    return evaluation result as pd.DF, columns are defined by evaluator
    """
    results = {}
    for (kind, name), model in df_cv.best_model.iteritems():
        results[kind,name] = evaluator(model, train_x, train_y, test_x, test_y)

    df_results = pd.DataFrame(results).T
    if 'test_f1' in df_results.columns:
        df_results.sort_values(by='test_f1', ascending=False, inplace=True)

    if save_res:
        df_results.to_csv(os.path.join(path, 'cv_%d_best_models_evaluation.csv' % cv))

    return df_results


def evaluator_scalable_cls(model, train_x, train_y, test_x, test_y):
    """
    Evaluator for scalable classification. E.g. Ys are 1, 2, 3, 4
    Both regression and classification will be used.
    prediction by regression will be round up (bounded by max and min of Ys) as a class label
    :return: metrics: mse, accuracy and weighted f1, for both train and test
    """
    min_y, max_y = train_y.min(), train_y.max()

    model.fit(train_x, train_y)

    train_pred = model.predict(train_x)
    train_pred_round = bounded_round(train_pred, min_y, max_y)

    mse_train = mean_squared_error(train_y, train_pred)
    acc_train = accuracy_score(train_y, train_pred_round)
    f1_train = f1_score(train_y, train_pred_round, average='weighted')

    test_pred = model.predict(test_x)
    test_pred_round = bounded_round(test_pred, min_y, max_y)

    mse_test = mean_squared_error(test_y, test_pred)
    acc_test = accuracy_score(test_y, test_pred_round)
    f1_test = f1_score(test_y, test_pred_round, average='weighted')

    result = {
        'train_f1': f1_train,
        'train_acc': acc_train,
        'train_mse': mse_train,
        'test_f1': f1_test,
        'test_acc': acc_test,
        'test_mse': mse_test,
    }
    return result


# ################################################
# Visualization cross validation result
# ################################################

def vis_evaluation(path, cv):
    df_eval = pd.read_csv(os.path.join(path, 'cv_%d_best_models_evaluation.csv' % cv))
    return df_eval.plot()


def vis_grid_cv_one_model(fn):
    df = pd.read_csv(fn, index_col=0)
    return df[['mean_test_score', 'mean_train_score']].boxplot()


















