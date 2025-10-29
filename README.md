# judge-total

Sharif-Judge の Final Submissions の Excel データからスコア一覧の csv ファイルを生成します。

---

## judge-total.py - Excel to CSV 変換

### 機能

Sharif-Judge の Final Submissions からエクスポートした Excel ファイル（.xls または .xlsx）を読み込み、ユーザーごとの得点一覧を CSV に出力します。

## Requirements

- Python3
- Pandas
  - .xlsx の読み込みには通常 openpyxl が必要です: `pip install openpyxl`
  - .xls の読み込みには xlrd が必要な場合があります: `pip install xlrd`
  - **注意**: 古い .xls ファイル（Excel 95/97-2003形式）は xlrd でも読めない場合があります。その場合は Excel や LibreOffice で .xlsx に変換してから使用してください。

## How to Use

> $ python3 judge-total.py [EXCEL_FILE]

- EXCEL_FILE を省略した場合、カレントディレクトリの judge_final_submissions.xlsx を読み込みます。
- .xls または .xlsx のいずれにも対応しています（.xls は環境によって xlrd のインストールが必要）。
- judge_final_submissions.xlsx の1行目にある Assignments 名と日時をファイル名としたスコア一覧 csv ファイルをカレントディレクトリに出力します。
- 教員やTAユーザーなど、一覧から除外したいユーザーを users で定義してますので適宜修正して下さい。除外ユーザーは前方一致で定義しています。

## 除外ユーザーの設定

- 除外したいユーザー名の「プレフィックス」を `exclude_users.txt` に1行ずつ記述してください（例: `ta`, `student` など）。
- 行頭が `#` の行はコメント、空行は無視されます。
- 既定のファイルは `exclude_users.txt` ですが、`-e/--exclude-file` で別パスを指定できます。

### 例: exclude_users.txt

```text
# prefixes of usernames to exclude (one per line)
ta
y24m
y25m
student
sano
```

### 別の除外ファイルを指定する（fish）

```fish
python3 judge-total.py -e ./my_excludes.txt
```

### Examples (fish)

```fish
# デフォルトのファイル名を使う
python3 judge-total.py

# 明示的にファイルを指定する
python3 judge-total.py ./some_dir/submissions.xlsx
python3 judge-total.py ./old_format.xls
```

## トラブルシューティング

### .xls ファイルの読み込みエラー

古い Excel 形式（.xls）の読み込みで以下のようなエラーが出る場合:

```text
Error: .xls ファイルの読み込みに失敗しました。
```

**対処法:**

1. **xlrd をインストール**:

   ```fish
   pip install xlrd
   ```

2. **それでも失敗する場合（古い .xls ファイルの場合）**:
   - Excel や LibreOffice Calc でファイルを開き、`.xlsx` 形式で保存し直してください
   - または、以下のコマンドで変換できます（LibreOffice がインストールされている場合）:

     ```fish
     libreoffice --headless --convert-to xlsx network-test2.xls
     ```

---

## judge-merge-csv.py - CSV マージツール

### 機能

`judge-total.py` で生成された複数の CSV ファイルをユーザーごとにマージし、1つの統合 CSV ファイルを作成します。

### 使い方

```fish
python3 judge-merge-csv.py [CSV_FILES...]
```

- `CSV_FILES`: マージしたい CSV ファイルのパス（複数指定可、必須）
- `-o/--output`: 出力ファイル名（省略時は入力ファイルの共通プレフィックス + `_merged.csv`）

### 動作仕様

1. **ファイル識別子の抽出**: 各ファイル名から日時部分（`_YYYYMMDD-HHMMSS`）を除いたプレフィックスを抽出
  - 例: `test2_20251029-123627.csv` → `test2`
2. **列名のリネーム**: 各CSVの `User` 列以外のすべての列にファイル識別子をプレフィックスとして付与
  - 例: `1 (Problem )` → `test2_1 (Problem )`
3. **マージ**: `User` 列をキーに全ファイルを外部結合（outer join）
4. **欠損値処理**: マージ後の欠損値（NaN）は 0.0 で埋める
5. **出力**: `User` でソートして CSV 出力

### 使用例（fish）

```fish
# 2つのCSVファイルをマージ（出力: test_merged.csv）
python3 judge-merge-csv.py test1_20251028-100000.csv test2_20251029-123627.csv

# ワイルドカードで複数ファイルを指定
python3 judge-merge-csv.py exam*.csv

# 出力ファイル名を明示的に指定
python3 judge-merge-csv.py -o final_scores.csv test1.csv test2.csv test3.csv

# ディレクトリを跨いで指定
python3 judge-merge-csv.py ./2024/test1.csv ./2025/test2.csv
```

### 入出力例

**入力1: test1_20251028-100000.csv**

```csv
,User,1 (Problem ),Total
0,y230001,10.0,10.0
1,y230002,8.0,8.0
2,y230003,9.0,9.0
```

**入力2: test2_20251029-123627.csv**

```csv
,User,2 (Problem ),Total
0,y230001,7.0,7.0
1,y230002,10.0,10.0
2,y230004,6.0,6.0
```

**出力: test_merged.csv**

```csv
User,test1_1 (Problem ),test1_Total,test2_2 (Problem ),test2_Total
y230001,10.0,10.0,7.0,7.0
y230002,8.0,8.0,10.0,10.0
y230003,9.0,9.0,0.0,0.0
y230004,0.0,0.0,6.0,6.0
```

### オプション

- `-h, --help`: ヘルプを表示
- `-o OUTPUT, --output OUTPUT`: 出力ファイル名を指定
