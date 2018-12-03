import pandas as pd
import json


SURVEY_DICT= {
    'bk_purpose': ['No Info', 'Mainly utility biking – traveling from one location to another', 'Mainly recreational biking – biking for recreation, leisure, and health', '50% utility, 50% recreational'],
    'age': ['No Info', '< 18', '18-24', '25-34', '35-44', '45-54', '55-64', '65-74', '>=75',],
    'ethnicity': ['No Info', 'White', 'Hispanic or Latino', 'Black or African American', 'Native American or American Indian', 'Asian / Pacific Islander', 'Other',],
    'edu': ['No Info', 'Nursery school to some high school, no diploma', 'High school graduate, diploma or the equivalent (for example: GED)', 'Some college credit, no degree', 'Associate degree', 'Bachelor’s degree', 'Master’s degree', 'Doctorate degree'],
    'marital': ['No Info', 'Single, never married', 'Married or domestic partnership', 'Widowed', 'Divorced', 'Separated'],
    'gender': ['No Info', 'Female', 'Male', 'Transgender – Female', 'Transgender – Male', 'Gender-variant / Non-conforming', 'Not listed', ],
    'driver': ['no', 'yes', 'No Info',],
    'car': ['no', 'yes', 'No Info',],
    'household_income': ['No Info', 'Less than $24,999', '$25,000 to $39,999', '$40,000 to $54,999', '$55,000 to $69,999', '$70,000 to $84,999', '$85,000 to $99,999', '$100,000 to $149,999', '$150,000 or more'],
    'residence': ['No Info', 'Never', '<3 months', '3-6 months', '6-12 months', '1-3 years', '>=3 years'],
    'bk_type': ['No Info', 'CaBi Bike (Shared bike in the DC region)', 'Road Bike', 'Mountain Bike', 'Hybrid Bike', 'Cruiser Bike', 'BMX Bike', 'Folding Bike', 'Recumbent Bike', 'Tandem Bike', 'Do not ride a bike', 'bk_type_other'],
}
SURVEY_COLS = ['bk_purpose', 'age', 'ethnicity', 'edu', 'marital', 'gender', 'driver','car', 'household_income', 'residence', 'bk_type']

def weighted_seg_score(df, col_name='csl', score_col='score'):
    if df.shape[0]==0:
        return pd.DataFrame()
    score = df.groupby('index_seg').apply(lambda x: (x[score_col]* x.ratio).sum()/x.ratio.sum()).to_frame()
    score.columns = [col_name]
    return score

def large_joint_table(date='2017-08-30', verbose=False):

    fn = 'DB-backup/%s/cyclings_vid1.json' % date
    data = json.load(open(fn))
    dfs = {}
    for i, item in enumerate(data):
        if item['type']=='table':
            name = item['name']
            if name not in ( 'video2seg_temp'):
                if verbose: print(i,item['name'])
                dfs[name] = pd.DataFrame(item['data'])
    users = dfs['Users'].rename(columns={'user_id': 'uid'})
    ratings = dfs['Rating'].drop('email', axis=1)
    videos=dfs['Video']
    videos.URL = videos.URL.apply(lambda x: 'https://www.youtube.com/watch?v='+x)
    vid2seg = dfs['VideoRoadSeg']
    segs = dfs['RoadSegment']
    nontest_users = users[~users.email.str.contains('test')]
    nontest_uid = nontest_users.uid
    print('with test', ratings.shape)
    ratings = ratings[ratings.uid.isin(nontest_uid)]
    print('without test users', ratings.shape)

    joint_table = ratings.merge(vid2seg[['vid', 'index_seg', 'ratio']]\
                         .merge(segs[['index_seg', 'geometry']])\
                         .merge(videos[['vid','URL']])).merge(users)
    joint_table.ratio = joint_table.ratio.astype(float) 
    joint_table.score = joint_table.score.astype(float)
    return joint_table

def get_dfs(date='2017-10-01'):
    dfs = {}
    for name in ['loginLog', 'Rating', 'RoadSegment', 'Users', 'Video', 'VideoRoadSeg']:
        dfs[name] = pd.read_csv('DB-backup/%s/%s.csv' %(date, name), index_col=0)
    return dfs
    
def load_joint_table2(date='2017-10-01'):
    dfs = {}
    for name in ['loginLog', 'Rating', 'RoadSegment', 'Users', 'Video', 'VideoRoadSeg']:
        dfs[name] = pd.read_csv('DB-backup/%s/%s.csv' %(date, name), index_col=0)
    
    users = dfs['Users'].rename(columns={'user_id': 'uid'})
    users.email.fillna('', inplace=True)
    ratings = dfs['Rating'].drop('email', axis=1)
    videos=dfs['Video']
    videos.URL = videos.URL.apply(lambda x: 'https://www.youtube.com/watch?v='+x)
    vid2seg = dfs['VideoRoadSeg']
    segs = dfs['RoadSegment']
    nontest_users = users[~users.email.str.contains('test')]
    nontest_uid = nontest_users.uid
    print('with test', ratings.shape)
    ratings = ratings[ratings.uid.isin(nontest_uid)]
    print('without test users', ratings.shape)

    joint_table = ratings.merge(vid2seg[['vid', 'index_seg', 'ratio']]\
                         .merge(segs[['index_seg', 'geometry']])\
                         .merge(videos[['vid','URL']])).merge(users)
    joint_table.ratio = joint_table.ratio.astype(float) 
    joint_table.score = joint_table.score.astype(float)
    return joint_table
