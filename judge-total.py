#!/usr/bin/python3

import argparse
import sys
from pathlib import Path

def read_excel_file(path: str, header=None):
    """Excel ファイルを拡張子に応じて読み込む（.xls/.xlsx 対応）。
    .xls の場合は複数のエンジンを試行します。
    """
    suffix = Path(path).suffix.lower()
    errors = []
    
    # .xls の場合は複数エンジンを試行
    if suffix == '.xls':
        # まず xlrd を試す
        for engine in ['xlrd', 'openpyxl', None]:
            try:
                if engine:
                    return pd.read_excel(path, header=header, engine=engine)
                else:
                    return pd.read_excel(path, header=header)
            except Exception as e:
                errors.append(f"{engine or 'default'}: {e}")
                continue
        # すべて失敗
        print(f"Error: .xls ファイルの読み込みに失敗しました。", file=sys.stderr)
        print(f"  ファイル: {path}", file=sys.stderr)
        print(f"  試行したエンジン: xlrd, openpyxl, default", file=sys.stderr)
        for err in errors:
            print(f"    - {err}", file=sys.stderr)
        print(f"\n対処法:", file=sys.stderr)
        print(f"  1. xlrd をインストール: pip install xlrd", file=sys.stderr)
        print(f"  2. 古い .xls の場合、Excel や LibreOffice で .xlsx に変換してください", file=sys.stderr)
        sys.exit(1)
    
    # .xlsx の場合
    try:
        return pd.read_excel(path, header=header)
    except Exception as e:
        print(f"Error: Excel ファイルの読み込みに失敗しました: {e}", file=sys.stderr)
        print(f"  ファイル: {path}", file=sys.stderr)
        print(f"\n対処法: openpyxl をインストール: pip install openpyxl", file=sys.stderr)
        sys.exit(1)


# 引数処理（未指定ならデフォルトファイルを使用）
parser = argparse.ArgumentParser(description='Sharif-Judge Final Submissions の Excel からスコア一覧 CSV を生成します。')
parser.add_argument('excel_file', nargs='?', default='judge_final_submissions.xlsx',
                    help='入力の Excel ファイル（.xls または .xlsx）。未指定時は judge_final_submissions.xlsx を使用')
parser.add_argument('-e', '--exclude-file', default='exclude_users.txt',
                    help='除外するユーザー名のプレフィックスを1行ずつ定義したテキストファイルのパス。未指定時は exclude_users.txt')
args = parser.parse_args()

infile = args.excel_file
excludefile = args.exclude_file
ext = Path(infile).suffix.lower()
if ext not in ('.xls', '.xlsx'):
    print("Error: 入力ファイルは .xls または .xlsx を指定してください。", file=sys.stderr)
    sys.exit(1)
if not Path(infile).exists():
    print(f"Error: 入力ファイルが見つかりません: {infile}", file=sys.stderr)
    sys.exit(1)

# 除外ファイル読み込み（pandas なしで可能）
def load_exclude_prefixes(path: str):
    p = Path(path)
    if not p.exists():
        # ファイルが無い場合は空の設定として続行
        print(f"Warning: 除外設定ファイルが見つかりませんでした（{path}）。除外せずに処理します。", file=sys.stderr)
        return tuple()
    prefixes = []
    for line in p.read_text(encoding='utf-8').splitlines():
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        prefixes.append(s)
    return tuple(prefixes)

exclude_prefixes = load_exclude_prefixes(excludefile)

# ここから先は Pandas が必要
import pandas as pd

# エクセルファイル読み込み（ヘッダ解析用）
df = read_excel_file(infile, header=None)

# ヘッダ解析
exName = df.iat[0,1]
exDate = str(df.iat[1,1]).replace('-','').replace(' ', '-').replace(':', '')
exFname = f'{exName}_{exDate}'

# データ部を再読み込み
df = read_excel_file(infile, header=5)
#print(df)

# ユーザーリスト（除外設定を適用）
user_series = df['Username'].astype(str).fillna('')
if exclude_prefixes:
    mask = ~user_series.str.startswith(exclude_prefixes)
else:
    # 除外設定が空なら全員を対象（空文字は除外）
    mask = user_series != ''
users = df[mask]['Username'].unique()
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
total_df=pd.DataFrame(tdf.select_dtypes(include=['number']).sum(axis=1),columns=['Total'])
tdf = pd.concat([tdf, total_df],axis=1)

# CSVに書き出し
print(tdf)
tdf.to_csv(f'{exFname}.csv')
print(f"\nWrite out {exFname}.csv")
