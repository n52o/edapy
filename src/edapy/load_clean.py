from __future__ import annotations
import pandas as pd


def load(
    file_path: str, preview: bool = False, head_rows: int = 5
) -> pd.DataFrame:
  df = pd.read_csv(file_path)

  dups = int(df.duplicated().sum())
  if dups > 0:
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"Duplicates: {dups} -> Removed.")
  else:
    print("Duplicates: 0 -> Nothing removed.")

  missing = df.isnull().sum()
  total_missing = int(missing.sum())
  print(f"Missing values: {total_missing}")
  if total_missing > 0:
    print(missing[missing > 0])

  print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")

  if preview:
    short_df = df.head(head_rows).copy()
    short_df.columns = [
        f"{str(c)[:18]}..." if len(str(c)) > 20 else str(c)
        for c in short_df.columns
    ]
    print(f"\nPreview (first {head_rows} rows):")
    print(short_df.to_string(index=False, max_cols=5))

  return df