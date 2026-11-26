import pandas as pd


def _to_numeric(series: pd.Series, col_name: str) -> pd.Series:
  if pd.api.types.is_numeric_dtype(series):
    return series.dropna().astype(float)

  as_num = pd.to_numeric(series, errors="coerce")
  if as_num.notna().mean() >= 0.8:
    print(f"Note: '{col_name}' converted from text to numeric.")
    return as_num.dropna().astype(float)

  codes, uniques = pd.factorize(series.dropna(), sort=True)
  mapping = {val: idx for idx, val in enumerate(uniques)}
  print(f"Note: '{col_name}' is text -> encoded to numbers: {mapping}")
  return pd.Series(codes, index=series.dropna().index, dtype=float)


def stats(
    df: pd.DataFrame, column: str, decimals: int = 2, show: bool = True
) -> dict:
  if column not in df.columns:
    raise KeyError(f"Column '{column}' not found.")

  s = _to_numeric(df[column], column)
  q1 = s.quantile(0.25)
  median = s.quantile(0.50)
  q3 = s.quantile(0.75)
  iqr = q3 - q1
  lower = q1 - 1.5 * iqr
  upper = q3 + 1.5 * iqr
  outliers = s[(s < lower) | (s > upper)]

  res = {
      "sum": round(float(s.sum()), decimals),
      "mean": round(float(s.mean()), decimals),
      "median": round(float(median), decimals),
      "q1": round(float(q1), decimals),
      "q3": round(float(q3), decimals),
      "iqr": round(float(iqr), decimals),
      "lower_bound": round(float(lower), decimals),
      "upper_bound": round(float(upper), decimals),
      "outliers_count": int(outliers.count()),
  }

  if show:
    print(f"\n--- {column} ---")
    for k, v in res.items():
      print(f"{k}: {v}")

  return res