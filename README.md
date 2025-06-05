# sqlgen

A Python utility to convert CSV files or pandas DataFrames into SQL `INSERT` statements.

## Features

- ✅ Supports both CSV files and pandas DataFrames
- ✅ Outputs standard SQL INSERT statements
- ✅ Batching via `rows_per_insert`
- ✅ Handles NULL values
- ✅ Optional progress bar with `tqdm`
- ✅ Splits output files by size (`max_file_size_mb`)
- ✅ Table name and column name inference or manual override
- ✅ Compact SQL output (`compact_sql=True`)

## Installation

```bash
pip install pandas
pip install tqdm  # optional
```

## Usage

```python
# From CSV
from sqlgen import to_sql

# Basic usage from CSV
sql_lines = to_sql(
    input_data="example.csv",     # CSV file path
    table_name="my_table",        # Optional: table name (defaults to filename)
    output_dir="output_sqls",     # Output directory
    max_file_size_mb=5,           # Split into files up to 5MB each
    rows_per_insert=500,          # Batch insert size
    compact_sql=True,             # Remove spaces between values
    preview=True,                 # Print first few lines of SQL
    use_progress_bar=True         # Show progress bar with tqdm
)

# From DataFrame
import pandas as pd
from sqlgen import to_sql

# Create DataFrame
df = pd.DataFrame({
    "id": [1, 2],
    "name": ["Alice", "Bob"],
    "age": [25, None]
})

# Convert DataFrame to SQL INSERT statements
sql_lines = to_sql(
    input_data=df,
    table_name="users",
    output_dir="output_sqls",
    compact_sql=False,            # Keep spaces between values
    use_progress_bar=True,        # Show progress bar
    null_values=["", "null"]      # Treat empty strings or 'null' as NULL
)
```

## License

MIT License. See [LICENSE](./LICENSE) for details.
