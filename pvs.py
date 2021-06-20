from api import Phoenix, Postgres
import pandas as pd
import numpy as np
ph =        Phoenix()
po =        Postgres('main')

def update_data_vf(): 
    query = open('target_query.sql', 'r').read()
    df = ph.get_df(query)
    df.to_sql('target_sample',if_exists='replace', index=False, con=po.sa_con())
#update_data_vf()

#DATAFRAMES
df_poll = pd.read_sql('data_poll', index_col='index', con=po.sa_con())
df_vf = pd.read_sql('target_sample', index_col='rand', con=po.sa_con())
df_vf = df_vf.drop(['delta_gov_recent_prez_16', 'gov_2_way_recent', 'is_vote_g_18','is_vote_g_18_none','is_vote_g_18_illeg'], axis=1)
df_vf = df_vf.replace({np.nan:0})

#FEATURES
var_target = 'variance' #output of compile.def_var()
df_poll_x = df_poll.drop(var_target, axis=1)
#df_poll_x = df_poll_x.drop('partisan_score', axis=1)
df_poll_x = pd.DataFrame(df_poll_x.partisan_score)
df_poll_y = df_poll[var_target]

def model_var(xs,ys):
    from sklearn.model_selection import GridSearchCV
    from sklearn.ensemble import RandomForestClassifier

    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report

    random_state =      19920217

    parameters = {
    'max_depth':[5,10,20,40,80],
    'n_estimators':[150,200,250,300]
    }

    xtrain, xtest, ytrain, ytest =      train_test_split(xs,ys, test_size=.15, random_state=random_state)

    clf =       GridSearchCV(rfc, parameters)
    clf.fit(xtrain,ytrain)
    print(classification_report(ytest,clf.predict(xtest)))

    param_results = pd.DataFrame(clf.cv_results_)
    param_results.to_csv(r'gscv_rfc.csv', index=False)

    return clf 

#model_var(df_poll_x,df_poll_y)

print('df_poll_x: ',[x for x in df_poll_x.columns.to_list()],'\n\n')
clf_var = model_var(df_poll_x,df_poll_y)

#PREDICT VF
df_vf_x = df_vf[df_poll_x.columns.to_list()] #MAKES VF COLS = POLL COLLS FOR PREDICTION
df_vf_x.reset_index(inplace=True, drop=True)
df_vf_y = clf_var.predict_proba(df_vf_x)
vfy = pd.DataFrame(df_vf_y, columns=['zero','one','two','three','four'])

#TRANSFORM PREDICTION
y = (vfy.one * 1) + (vfy.two * 2) + (vfy.three * 3) + (vfy.four * 4) #cumulative weight/sum of probability of being undecided/persuadeable
y.rename('nonnormal_y', inplace=True)
ymm = (y - y.min()) / (y.max() - y.min()) #normalize y
ymm.rename('normal_y', inplace=True)


#JOIN DF TO DEPENDENT VARIABLES
df = pd.concat([df_vf_x,y,ymm], axis=1)

#CLEAN DF 
df.replace(0, np.nan, inplace=True)
df.replace({'is_dem':{1.0:'DEM'}, 
            'is_gop':{1.0:'REP'}, 
            'is_npa':{1.0:'NPA'}, 
            'is_male':{1.0:'MALE'}, 
            'is_female':{1.0:'FEMALE'}},
            inplace=True)


df['sex'] = df.is_male.fillna('') + df.is_female.fillna('')
df['party'] = df.is_dem.fillna('') + df.is_gop.fillna('') + df.is_npa.fillna('')

df.drop(['is_male', 'is_female', 'is_dem', 'is_gop', 'is_npa'], axis=1, inplace=True)

df = df[['age', 'party', 'sex', 'partisan_score', 'nonnormal_y', 'normal_y']]

df.to_csv(r'score_persuasion_sample.csv', index=False)

from joblib import dump, load
dump(clf_var, 'model_persuasion.joblib')



