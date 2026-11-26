from __future__ import annotations
from pathlib import Path
from typing import Union
import numpy as np
import pandas as pd

_MISSING_TOKENS = {
    "",
    "na",
    "n/a",
    "nan",
    "null",
    "none",
    "nil",
    "-",
    "--",
    "?",
    "unknown",
}


def _read_any_file(file_path: Union[str, Path, pd.DataFrame]) -> pd.DataFrame:
  if isinstance(file_path, pd.DataFrame):
    return file_path.copy()

  path = Path(file_path)
  if not path.exists():
    raise FileNotFoundError(f"File not found: {path}")

  suffix = path.suffix.lower()

  if suffix in {".xlsx", ".xls"}:
    try:
      return pd.read_excel(path)
    except ImportError as exc:
      raise ImportError(
          "Reading Excel files requires 'openpyxl'. Install it via: pip install"
          " openpyxl"
      ) from exc

  if suffix == ".json":
    return pd.read_json(path)

  last_err = None
  for enc in ("utf-8", "utf-8-sig", "cp1256", "latin1"):
    try:
      df = pd.read_csv(path, encoding=enc)
      if df.shape[1] == 1:
        df_auto = pd.read_csv(path, encoding=enc, sep=None, engine="python")
        if df_auto.shape[1] > 1:
          return df_auto
      return df
    except Exception as err:
      last_err = err

  raise ValueError(f"Could not decode or parse '{path}': {last_err}")


def load(
    file_path: Union[str, Path, pd.DataFrame],
    preview: bool = False,
    head_rows: int = 5,
) -> pd.DataFrame:
  df = _read_any_file(file_path)

  # Clean column names
  df.columns = [str(c).strip() for c in df.columns]

  # Normalize hidden missing tokens in text columns
  for col in df.select_dtypes(include=["object", "string"]).columns:
    stripped = df[col].astype(str).str.strip()
    mask = stripped.str.lower().isin(_MISSING_TOKENS) & df[col].notna()
    if mask.any():
      df.loc[mask, col] = np.nan

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