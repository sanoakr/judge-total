#!/usr/bin/python3

import argparse
import sys
from pathlib import Path
import pandas as pd
import os
import glob


def extract_common_prefix(filenames):
    """ファイル名のリストから共通プレフィックスを抽出する。"""
    if not filenames:
        return "merged"
    
    # ベース名のみを使用（ディレクトリ部分を除く）
    basenames = [Path(f).stem for f in filenames]
    
    if len(basenames) == 1:
        return basenames[0]
    
    # 共通プレフィックスを探す
    prefix = os.path.commonprefix(basenames)
    # 末尾の区切り文字やアンダースコアをトリム
    prefix = prefix.rstrip('_- ')
    
    return prefix if prefix else "merged"


def extract_file_identifier(filepath):
    """ファイルパスからファイル識別子を抽出（日時部分を除いたプレフィックス）。
    例: "test2_20251029-123627.csv" -> "test2"
    """
    stem = Path(filepath).stem
    # 日時パターン（YYYYMMDD-HHMMSS）を除去
    import re
    # アンダースコアの後に日時パターンがある場合、それを除去
    pattern = r'_\d{8}-\d{6}$'
    identifier = re.sub(pattern, '', stem)
    return identifier if identifier else stem


def merge_csv_files(csv_files):
    """複数のCSVファイルを読み込み、Userごとにマージする。"""
    if not csv_files:
        print("Error: CSVファイルが指定されていません。", file=sys.stderr)
        sys.exit(1)
    
    # 各ファイルを読み込み
    dataframes = []
    file_identifiers = []
    
    for csv_file in csv_files:
        if not Path(csv_file).exists():
            print(f"Error: ファイルが見つかりません: {csv_file}", file=sys.stderr)
            sys.exit(1)
        
        try:
            # 最初の列（インデックス列）を無視して読み込み
            df = pd.read_csv(csv_file, index_col=0)
            identifier = extract_file_identifier(csv_file)
            
            # 各ファイル内の "Total" 列は使用しないため除去
            if 'Total' in df.columns:
                df = df.drop(columns=['Total'])

            # User列以外の列名にファイル識別子をプレフィックスとして追加
            rename_dict = {}
            for col in df.columns:
                if col != 'User':
                    rename_dict[col] = f"{identifier}_{col}"
            
            df = df.rename(columns=rename_dict)
            dataframes.append(df)
            file_identifiers.append(identifier)
            
            print(f"読み込み: {csv_file} ({len(df)} users)")
            
        except Exception as e:
            print(f"Error: CSVファイルの読み込みに失敗しました: {csv_file}", file=sys.stderr)
            print(f"  {e}", file=sys.stderr)
            sys.exit(1)
    
    # Userをキーにしてマージ
    print(f"\n{len(dataframes)} 個のファイルをマージ中...")
    merged = dataframes[0]
    for i, df in enumerate(dataframes[1:], 1):
        merged = merged.merge(df, on='User', how='outer')
    
    # User列を先頭に
    cols = ['User'] + [col for col in merged.columns if col != 'User']
    merged = merged[cols]
    
    # ユーザーごとの合計（全問題列の数値合計）と非空セル数を末尾に追加
    # 数値列のみを対象にする
    numeric_df = merged.select_dtypes(include=['number'])
    total_series = numeric_df.sum(axis=1, skipna=True)
    count_series = numeric_df.count(axis=1)

    merged['Total'] = total_series
    merged['Count'] = count_series

    # 列順: User -> 既存の問題列 -> Total -> Count
    cols = ['User'] + [c for c in merged.columns if c not in ('User', 'Total', 'Count')] + ['Total', 'Count']
    merged = merged[cols]

    # Userでソート
    merged = merged.sort_values('User').reset_index(drop=True)
    
    return merged, file_identifiers


def main():
    parser = argparse.ArgumentParser(
        description='複数のCSVファイル（judge-total.py の出力）をユーザーごとにマージします。'
    )
    parser.add_argument(
        'csv_files',
        nargs='+',
        help='マージするCSVファイルのパス（複数指定可）'
    )
    parser.add_argument(
        '-o', '--output',
        help='出力CSVファイル名。未指定時は入力ファイルの共通プレフィックス + "_merged.csv"'
    )
    
    args = parser.parse_args()
    
    # 引数にワイルドカードが含まれている場合に対応して展開
    expanded_files = []
    for pat in args.csv_files:
        matches = glob.glob(pat)
        if matches:
            expanded_files.extend(matches)
        elif Path(pat).exists():
            expanded_files.append(pat)
        else:
            print(f"Warning: パターンに一致するファイルがありませんでした: {pat}", file=sys.stderr)

    # 重複除去（順序保持）
    seen = set()
    files = []
    for f in expanded_files:
        if f not in seen:
            files.append(f)
            seen.add(f)

    if not files:
        print("Error: マージ対象のCSVファイルが見つかりません。", file=sys.stderr)
        sys.exit(1)

    print("対象ファイル:")
    for f in files:
        print(f"  - {f}")

    # マージ実行
    merged_df, identifiers = merge_csv_files(files)
    
    # 出力ファイル名を決定
    if args.output:
        output_file = args.output
    else:
        common_prefix = extract_common_prefix(args.csv_files)
        output_file = f"{common_prefix}_merged.csv"
    
    # CSV出力
    merged_df.to_csv(output_file, index=False)
    print(f"\n✓ マージ完了: {output_file}")
    print(f"  総ユーザー数: {len(merged_df)}")
    print(f"  総列数: {len(merged_df.columns)}")
    print(f"\nプレビュー:")
    print(merged_df.head(10))


if __name__ == '__main__':
    main()
