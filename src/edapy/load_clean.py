from __future__ import annotations
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
  print(f"Missing values: {total_missing}")
  if total_missing > 0:
    print(missing[missing > 0])

  print(f"\nFirst {head_rows} rows ({df.shape[0]} rows x {df.shape[1]} cols):")
  with pd.option_context("display.max_columns", 8, "display.width", 110):
    print(df.head(head_rows))

  return df