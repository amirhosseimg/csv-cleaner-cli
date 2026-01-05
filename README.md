# csv-cleaner-cli

A tiny Python CLI to clean and filter CSV files (no pandas required).

# Features:
- Select columns (--select)

- Filter rows (--where)

- Drop missing values (--dropna)

- Overwrite output (--overwrite)

- Works without pandas


## Examples

### Keep only a few columns

python -m csvcleaner.cli input.csv output.csv --select name,age,country


### Filter rows
python -m csvcleaner.cli input.csv output.csv --where "age>=18"

### Drop rows with missing values in selected columns
python -m csvcleaner.cli input.csv output.csv --select name,age --dropna
