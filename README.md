# judge-total.py
Sharif-Judge の Final Submissions の Excel データからスコア一覧の csv ファイルを生成します。

## Requirements
- Python3
- Pandas

## How to Use
>  $ python3 judge-total.py

- Final Submission からダウンロードできる judge_final_submissions.xlsx をカレントディレクトリから読み込みます。他のファイルを読みたければコードを修正して下さい。
- judge_final_submissions.xlsx の1行目にある Assignments 名と日時をファイル名としたスコア一覧 csv ファイルをカレントディレクトリに出力します。
- 教員やTAユーザーなど、一覧から除外したいユーザーを users で定義してますので適宜修正して下さい。除外ユーザーは前方一致で定義しています。
