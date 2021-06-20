import pandasql as pasql
def s_unique(df): 
    for i, r in df.iteritems(): 
        print(r.unique())

def s_na(df): 
    for i, r in dc.iteritems(): 
        num = r.isna().sum()
        denom = len(r)
        if num / denom < .95: 
            if len(r.unique()) < 5: 
                print(i)
                print(i, ' #rec: ',  len(r), ', isna:  ',  r.isna().sum())

def concat_glub(path): 
    import pandas as pd 
    import glob
    glub = glob.glob(path)

    dfs = []

    for df in glub: 
        df = pd.read_csv(df) 
        dfs.append(df)

    dff_cols = ['GENVOTE', 'GOVVOTE', 'Party Registration', 'AGE', 'GENDER', 'tsmart_partisan_score']
    dff = pd.concat([x for x in dfs])
    dff = dff[dff_cols]
    dff = dff.rename({'Party Registration':'party', 
                      'AGE':'age', 
                       'tsmart_partisan_score':'partisan_score'}, axis=1)
    dff.columns = [x.lower() for x in dff.columns]
    dff['agel'] = dff['age'].astype(str).str[:2]
    dff['ageh'] = dff['age'].astype(str).str[-2:]
    dff['agel'] = dff['agel'].replace({r'(N':0, 'Ov':0,'na':0}).astype(int)
    dff['ageh'] = dff['ageh'].replace({r'r)':0, 'an':0}).astype(int)
    dff['age'] = (dff['ageh'] + dff['agel']) / 2
    dff.drop(['agel','ageh'], axis=1, inplace=True) 

    dff['age'] = (dff.age - dff.age.min()) / (dff.age.max() - dff.age.min())
    dff['partisan_score'] = (dff.partisan_score - dff.partisan_score.min()) / (dff.partisan_score.max() - dff.partisan_score.min())
    return dff

dfs = concat_glub('*.csv') #clean poll sample copy

query =         open('compile.sql','r+').read()
pysql =        lambda q : pasql.sqldf(q, globals())

da = pysql(query)
 
import numpy as np
def def_var(df): 
    if df.ball_generic == np.nan:
        return np.nan
    elif df.ball_gov == np.nan: 
        return np.nan
    elif df.ball_gov == 0 and df.ball_generic == 0:  
        return 4
    else: 
        return abs(df.ball_gov - df.ball_generic) #the target feature of the model 

da['variance'] = da.apply(def_var, axis=1)

da = da.drop(['ball_generic','ball_gov'], axis=1)
da = da.dropna(subset=['variance'], axis=0)
da = da.replace({np.nan:0})

from api import Postgres
po = Postgres('main')
da.to_sql('data_poll', con=po.sa_con(), if_exists='replace')
