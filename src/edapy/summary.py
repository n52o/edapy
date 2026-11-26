from __future__ import annotations
from typing import List, Optional
import pandas as pd
from .stats import stats


def summary(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    save_path: Optional[str] = "summary.csv",
    decimals: int = 2,
    show: bool = True,
) -> pd.DataFrame:
  cols = columns if columns is not None else list(df.columns)
  rows = []

  for col in cols:
    res = stats(df, col, decimals=decimals, show=False)
    rows.append({
        "Column": col,
        "Total": res["sum"],
        "Mean": res["mean"],
        "Median": res["median"],
        "Q1": res["q1"],
        "Q3": res["q3"],
        "IQR": res["iqr"],
        "Lower_Bound": res["lower_bound"],
        "Upper_Bound": res["upper_bound"],
        "Outliers": res["outliers_count"],
    })

  out = pd.DataFrame(rows)

  if save_path:
    out.to_csv(save_path, index=False)
    print(f"\nSummary CSV saved to: {save_path}")

  if show:
    max_len = int(out["Column"].astype(str).str.len().max())
    fmt = {"Column": lambda x: f"{str(x):<{max_len}}  "}
    print()
    print(
        out.to_string(index=False, justify="left", col_space=3, formatters=fmt)
    )

  return out