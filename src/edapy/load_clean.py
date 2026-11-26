import pandas as pd


def load(file_path: str, head_rows: int = 5) -> pd.DataFrame:
  df = pd.read_csv(file_path)

  dups = int(df.duplicated().sum())
  if dups > 0:
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"Duplicates: {dups} -> Removed.")
  else:
    print("Duplicates: 0 -> Nothing removed.")

  missing = df.isnull().sum()
  total_missing = int(missing.sum())
  print(f"\nMissing values: {total_missing}")
  if total_missing > 0:
    print(missing[missing > 0])

  print(f"\nFirst {head_rows} rows:")
  print(df.head(head_rows).to_string(index=False))

  return df