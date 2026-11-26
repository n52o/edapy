from __future__ import annotations
from typing import Any, Dict, Optional, Tuple
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


def _prepare_series(
    s: pd.Series,
) -> Tuple[pd.Series, str, Optional[Dict[str, int]]]:
  """Convert any column (numeric, dirty numeric, bool, datetime, categorical) into a numeric series."""
  if pd.api.types.is_bool_dtype(s):
    return s.astype("float64"), "boolean (0/1)", None

  if pd.api.types.is_numeric_dtype(s):
    return pd.to_numeric(s, errors="coerce"), "numeric", None

  if pd.api.types.is_datetime64_any_dtype(s):
    days = (s - pd.Timestamp("1970-01-01")) / pd.Timedelta(days=1)
    return pd.to_numeric(days, errors="coerce"), "datetime (days)", None

  # Clean text missing tokens first
  s_clean = s.copy()
  non_null_mask = s_clean.notna()
  stripped = s_clean[non_null_mask].astype(str).str.strip()
  missing_mask = stripped.str.lower().isin(_MISSING_TOKENS)
  if missing_mask.any():
    s_clean.loc[stripped[missing_mask].index] = np.nan

  valid = s_clean.dropna()
  if len(valid) == 0:
    return pd.Series(dtype="float64"), "empty", None

  # Try cleaning dirty numbers like "$1,250.50", "45%", "(500)", "200 EGP"
  cleaned_str = (
      valid.astype(str)
      .str.strip()
      .str.replace(r"^\((.+)\)$", r"-\1", regex=True)
      .str.replace(r"[,$€£¥%]", "", regex=True)
      .str.replace(
          r"\s*(egp|usd|sar|kwd|aed|eur|gbp|kg|km|kwh)$",
          "",
          case=False,
          regex=True,
      )
      .str.strip()
  )
  parsed_num = pd.to_numeric(cleaned_str, errors="coerce")

  if float(parsed_num.notna().mean()) >= 0.70:
    full_str = (
        s_clean.astype(str)
        .str.strip()
        .str.replace(r"^\((.+)\)$", r"-\1", regex=True)
        .str.replace(r"[,$€£¥%]", "", regex=True)
        .str.replace(
            r"\s*(egp|usd|sar|kwd|aed|eur|gbp|kg|km|kwh)$",
            "",
            case=False,
            regex=True,
        )
        .str.strip()
    )
    full_num = pd.to_numeric(full_str, errors="coerce")
    return full_num, "numeric (cleaned)", None

  # Try parsing date-like strings
  sample_str = valid.astype(str).str.strip()
  if sample_str.str.contains(r"[-/:]", regex=True).mean() >= 0.70:
    parsed_dt = pd.to_datetime(sample_str, errors="coerce")
    if float(parsed_dt.notna().mean()) >= 0.70:
      full_dt = pd.to_datetime(s_clean, errors="coerce")
      days = (full_dt - pd.Timestamp("1970-01-01")) / pd.Timedelta(days=1)
      return pd.to_numeric(days, errors="coerce"), "datetime (days)", None

  # Categorical / text auto-encoding
  codes, uniques = pd.factorize(s_clean)
  num_s = pd.Series(codes, index=s.index, dtype="float64").where(
      s_clean.notna(), np.nan
  )
  mapping = {str(val): int(idx) for idx, val in enumerate(uniques[:5])}
  return num_s, "categorical (auto-encoded)", mapping


def stats(
    df: pd.DataFrame, column: str, decimals: int = 2, show: bool = True
) -> Dict[str, Any]:
  if column not in df.columns:
    available = ", ".join(map(str, df.columns[:10]))
    raise ValueError(
        f"Column '{column}' not found. Available columns: [{available}]"
    )

  num_s, col_type, mapping = _prepare_series(df[column])
  clean = num_s.dropna()

  if len(clean) == 0:
    result: Dict[str, Any] = {
        "column": column,
        "type": "empty",
        "count": 0,
        "sum": None,
        "mean": None,
        "median": None,
        "q1": None,
        "q3": None,
        "iqr": None,
        "lower_bound": None,
        "upper_bound": None,
        "outliers_count": 0,
    }
    if show:
      print(f"\n--- Stats for '{column}' [empty column] ---")
    return result

  is_datetime = col_type.startswith("datetime")
  total = None if is_datetime else round(float(clean.sum()), decimals)
  mean = round(float(clean.mean()), decimals)
  median = round(float(clean.median()), decimals)
  q1 = round(float(clean.quantile(0.25)), decimals)
  q3 = round(float(clean.quantile(0.75)), decimals)
  iqr = round(q3 - q1, decimals)
  lower = round(q1 - 1.5 * iqr, decimals)
  upper = round(q3 + 1.5 * iqr, decimals)
  outliers_count = int(((clean < lower) | (clean > upper)).sum())

  result = {
      "column": column,
      "type": col_type,
      "count": int(len(clean)),
      "sum": total,
      "mean": mean,
      "median": median,
      "q1": q1,
      "q3": q3,
      "iqr": iqr,
      "lower_bound": lower,
      "upper_bound": upper,
      "outliers_count": outliers_count,
  }

  if show:
    print(f"\n--- Stats for '{column}' [{col_type}] ---")
    if mapping:
      preview_map = ", ".join(f"{k}={v}" for k, v in mapping.items())
      print(f"Encoding map (sample): {preview_map}")
    for k, v in result.items():
      if k not in ("column", "type"):
        print(f"  {k:<15}: {v}")

  return result