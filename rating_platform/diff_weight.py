import pandas as pd

def lvl_fearless_1st(lvl):
    """ ignore user with no exp lvl"""
    if pd.isnull(lvl):
        return 0
    return {'fearless': 4, 'confident': 3, 'interested': 2, 'reluctant': 1}[lvl]

def lvl_reluctant_1st(lvl):
    """ ignore user with no exp lvl"""
    if pd.isnull(lvl):
        return 0
    return {'fearless': 1, 'confident': 2, 'interested': 3, 'reluctant': 4}[lvl]

def familiar_include_no_info(fam):
    if pd.isnull(fam):
        return 2
    return {'no': 1, 'yes':3}[fam]

def familiar_exclude_no_info(fam):
    if pd.isnull(fam):
        return 0
    return {'no': 1, 'yes':2}[fam]
    
def ext_lvl_fearless_1st(lvl):
    """ ignore user with no exp lvl"""
    if pd.isnull(lvl):
        return 0
    return {'fearless': 100, 'confident': 66, 'interested': 33, 'reluctant': 1}[lvl]

def ext_lvl_reluctant_1st(lvl):
    """ ignore user with no exp lvl"""
    if pd.isnull(lvl):
        return 0
    return {'fearless': 1, 'confident': 33, 'interested': 66, 'reluctant': 100}[lvl]

def ext_familiar_include_no_info(fam):
    if pd.isnull(fam):
        return 50
    return {'no': 1, 'yes':100}[fam]

def ext_familiar_exclude_no_info(fam):
    if pd.isnull(fam):
        return 0
    return {'no': 1, 'yes':100}[fam]

def f4_c1_i1_r4(lvl):
    """ ignore user with no exp lvl"""
    if pd.isnull(lvl):
        return 0
    return {'fearless': 4, 'confident': 1, 'interested': 1, 'reluctant': 4}[lvl]
    
def f10_c1_i1_r10(lvl):
    """ ignore user with no exp lvl"""
    if pd.isnull(lvl):
        return 0
    return {'fearless': 10, 'confident': 1, 'interested': 1, 'reluctant': 10}[lvl]

def nf30_f1_unk1(fam):
    if pd.isnull(fam):
        return 1
    return {'no': 30, 'yes':1}[fam]

def nf30_f10_unk1(fam):
    if pd.isnull(fam):
        return 1
    return {'no': 30, 'yes':10}[fam]



def amplify_fcir(row):
    exp = row.experienceLevel
    score = row.score
    if exp=='fearless' and score<3:
        return score-1
    if exp=='confident' and score<4:
        return score-0.5
    if exp=='interested' and score>4:
        return score+0.5
    if exp=='reluctant' and score>3:
        return score+1
    return score


def amplify_fr(row):
    exp = row.experienceLevel
    score = row.score
    if exp=='fearless' and score<3:
        return score-1
    if exp=='reluctant' and score>3:
        return score+1
    return score