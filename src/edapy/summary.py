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
        "Type": res["type"],
        "Total": res["sum"] if res["sum"] is not None else "-",
        "Mean": res["mean"] if res["mean"] is not None else "-",
        "Median": res["median"] if res["median"] is not None else "-",
        "Q1": res["q1"] if res["q1"] is not None else "-",
        "Q3": res["q3"] if res["q3"] is not None else "-",
        "IQR": res["iqr"] if res["iqr"] is not None else "-",
        "Lower_Bound": (
            res["lower_bound"] if res["lower_bound"] is not None else "-"
        ),
        "Upper_Bound": (
            res["upper_bound"] if res["upper_bound"] is not None else "-"
        ),
        "Outliers": res["outliers_count"],
    })

  out = pd.DataFrame(rows)

  if save_path:
    out.to_csv(save_path, index=False)
    print(f"\nSummary CSV saved to: {save_path}")

  if show:
    max_col = int(out["Column"].astype(str).str.len().max())
    max_type = int(out["Type"].astype(str).str.len().max())
    fmt = {
        "Column": lambda x: f"{str(x):<{max_col}}  ",
        "Type": lambda x: f"{str(x):<{max_type}}  ",
    }
    print()
    print(
        out.to_string(index=False, justify="left", col_space=3, formatters=fmt)
    )

  return out