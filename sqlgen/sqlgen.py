import pandas as pd
import os
import csv
import math
from typing import List, Optional, Union


def wrap_progress(iterable, use_tqdm=True, **tqdm_kwargs):
    """tqdmがあれば進捗を表示し、なければそのまま返す"""
    if use_tqdm:
        try:
            from tqdm import tqdm
            return tqdm(iterable, **tqdm_kwargs)
        except ImportError:
            print("If you install pip install tqdm, you can display a progress bar.")
            pass
    return iterable

def escape(val: str, null_values: List[str]) -> str:
    """エスケープ処理（NULL, 数値, 文字列）"""
    if val is None or val.strip().lower() in null_values:
        return 'NULL'
    if val.endswith(".0"):
        try:
            return str(int(float(val)))
        except ValueError:
            pass
    try:
        int_val = int(val)
        return str(int_val)
    except ValueError:
        try:
            float_val = float(val)
            return str(float_val)
        except ValueError:
            return "'" + val.replace("'", "''") + "'"

def data_to_sql_lines(data: List[List[str]], table_name: str, cols: List[str], null_values: List[str], use_progress_bar: bool, compact_sql: bool = False, rows_per_insert: int = 1000) -> List[str]:
    """データをSQL INSERT文（複数バッチ）に変換"""
    column_string = ', '.join([f"`{col}`" for col in cols])
    sql_lines = []
    
    loop = wrap_progress(
        range(0, len(data), rows_per_insert),
        use_tqdm=use_progress_bar,
        desc="Generating INSERT statements"
    )
    for start in loop:
        batch = data[start:start+rows_per_insert]
        sql_lines.append(f"INSERT INTO `{table_name}` ({column_string}) VALUES")
        for i, row in enumerate(batch):
            if compact_sql:
                values = ','.join([escape(val, null_values) for val in row])
            else:
                values = ', '.join([escape(val, null_values) for val in row])

            suffix = ',' if i != len(batch) - 1 else ';'
            sql_lines.append(f"\t({values}){suffix}")
    return sql_lines

def decode_csv(input_path: str, custom_column_names: Optional[List[str]] = None) -> (List[str], List[List[str]]):
    """CSVファイルからヘッダーとデータを読み込み"""
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = list(csv.reader(f))
    if custom_column_names:
        if len(custom_column_names) != len(reader[0]):
            raise ValueError("custom_column_names must match the number of columns in the DataFrame")
        return custom_column_names, reader
    return reader[0], reader[1:]

def decode_df(df: pd.DataFrame, custom_column_names: Optional[List[str]] = None) -> (List[str], List[List[str]]):
    """DataFrameからヘッダーとデータ抽出"""
    df = df.fillna('')
    if custom_column_names:
        if len(custom_column_names) != len(df.columns):
            raise ValueError("custom_column_names must match the number of columns in the DataFrame")
        df = df.copy()
        df.columns = custom_column_names
        
    return df.columns.tolist(), df.astype(str).values.tolist()

def guess_table_name(input_data: Union[str, pd.DataFrame]) -> str:
    """ファイル名やDataFrameからテーブル名を推測"""
    if isinstance(input_data, str):
        return os.path.splitext(os.path.basename(input_data))[0]
    return "dataframe_table"  # DataFrameの変数名取得は不可能なので固定名

def split_sql_files(lines: List[str], output_dir: str, base_name: str, max_file_size_mb: int, use_progress_bar: bool):
    """SQL文をサイズごとに分割してファイル出力"""
    os.makedirs(output_dir, exist_ok=True)
    current_lines = []
    current_size = 0
    file_index = 1
    max_bytes = max_file_size_mb * 1024 * 1024
    
    loop = wrap_progress(lines, use_tqdm=use_progress_bar, desc="Writing SQL to files")

    for line in loop:
        line_bytes = len((line + '\n').encode('utf-8'))
        if current_size + line_bytes > max_bytes and current_lines:
            out_path = os.path.join(output_dir, f"{base_name}_{file_index}.sql")
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(current_lines))
            current_lines = []
            current_size = 0
            file_index += 1
        current_lines.append(line)
        current_size += line_bytes

    if current_lines:
        out_path = os.path.join(output_dir, f"{base_name}_{file_index}.sql")
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(current_lines))

def to_sql(
    input_data: Union[str, pd.DataFrame],
    table_name: Optional[str] = None,
    output_dir: str = "output_sqls",
    max_file_size_mb: int = 100,
    rows_per_insert: int = 100_000,
    null_values: List[str] = ["", "null", "NULL"],
    custom_column_names: Optional[List[str]] = None,
    preview: bool = False,
    use_progress_bar: bool = True,
    compact_sql: bool = False
):
    """統一されたCSV/DF→SQL変換関数"""
    if isinstance(input_data, pd.DataFrame):
        cols, data = decode_df(input_data, custom_column_names)
    elif isinstance(input_data, str):
        if input_data.endswith(".csv"):
            cols, data = decode_csv(input_data, custom_column_names)
        else:
            raise ValueError("Only .csv is supported for file inputs.")
    else:
        raise TypeError("input_data must be a CSV path or a pandas DataFrame.")

    table_name = table_name or guess_table_name(input_data)
    sql_lines = data_to_sql_lines(data, table_name, cols, null_values, use_progress_bar, compact_sql, rows_per_insert)

    if preview:
        print("\n".join(sql_lines[:10]))
        print("... (truncated)")

    base_name = table_name
    split_sql_files(sql_lines, output_dir, base_name, max_file_size_mb, use_progress_bar)
    return sql_lines  # for testability or chaining
