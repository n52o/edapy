import pandas as pd
import edapy


def test_stats_numeric():
    df = pd.DataFrame({"score": [10, 20, 30, 40, 100]})
    res = edapy.stats(df, "score", show=False)
    assert res["median"] == 30.0
    assert res["outliers_count"] == 1


def test_stats_categorical_auto_encode():
    df = pd.DataFrame({"grade": ["A", "B", "A", "C"]})
    res = edapy.stats(df, "grade", show=False)
    assert res["mean"] == 0.75


def test_summary_table(tmp_path):
    df = pd.DataFrame({"a": [1, 2, 3], "b": [10, 20, 30]})
    out_file = tmp_path / "out.csv"
    table = edapy.summary(df, save_path=str(out_file), show=False)
    assert len(table) == 2
    assert out_file.exists()