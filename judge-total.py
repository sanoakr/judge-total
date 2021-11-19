#!/usr/bin/python3

import pandas as pd

# エクセルファイル読み込み
df = pd.read_excel('judge_final_submissions.xlsx', header=None)

# ヘッダ解析
exName = df.iat[0,1]
exDate = df.iat[1,1].replace('-','').replace(' ', '-').replace(':', '')
exFname = f'{exName}_{exDate}'

# データ部を再読み込み
df = pd.read_excel('judge_final_submissions.xlsx', header=5)
#print(df)

# ユーザーリスト
users = df[~df['Username'].str.startswith(('ta','t20m','t21m','student','sano'))]['Username'].unique()
print(users)

# 問題リスト
probs = pd.Series(data=df['Problem'].unique())

# 総計用データフレーム
cols = pd.Series(data=['User'])
tdf = pd.DataFrame(index=[], columns=pd.concat([cols, probs]))
#print(tdf)

# ユーザーレコード追加
idx = 0
for u in users:
    tdf.loc[idx] = 0.0
    tdf.loc[idx, 'User'] = u
    idx += 1

# 得点を挿入
for row in df.itertuples():
    user = row.Username
    prob = row.Problem
    score =  row._12
    tdf.loc[tdf['User'] == user, prob] = score

# 総計を計算
tdf = pd.concat([tdf, pd.DataFrame(tdf.sum(axis=1),columns=['Total'])],axis=1)

# CSVに書き出し
print(tdf)
tdf.to_csv(f'{exFname}.csv')
print(f"\nWrite out {exFname}.csv")
