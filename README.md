# judge-total

[日本語](./README.ja.md) | English

CLI tools to process [Sharif Judge](https://github.com/ifaeit/sharif-judge) submission data for score reporting.

## Tools

### `judge-total.py` — Excel to CSV

Reads a Final Submissions Excel export (`.xls` or `.xlsx`) from Sharif Judge and outputs per-user score CSV files.

```fish
# Use default filename (judge_final_submissions.xlsx)
python3 judge-total.py

# Specify a file
python3 judge-total.py ./submissions.xlsx

# Use a custom exclude list
python3 judge-total.py -e ./my_excludes.txt
```

**Requirements:** Python 3, pandas, openpyxl (for `.xlsx`), xlrd (for `.xls`)

### `judge-merge-csv.py` — CSV Merge

Merges multiple score CSV files (output of `judge-total.py`) into a single CSV, joined by username.

```fish
python3 judge-merge-csv.py test1_*.csv test2_*.csv

# Specify output filename
python3 judge-merge-csv.py -o final_scores.csv *.csv
```

## Excluding Users

Add username prefixes (one per line) to `exclude_users.txt` to filter out instructors, TAs, etc.:

```
# exclude_users.txt
ta
student
sano
```

## Setup

```fish
pip install pandas openpyxl
# For .xls support:
pip install xlrd
```

## Related

- [sanoakr/Sharif-Judge-Docker](https://github.com/sanoakr/Sharif-Judge-Docker) — Dockerized Sharif Judge
