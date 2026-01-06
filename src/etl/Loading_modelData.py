import pandas as pd
from src.db.connect import get_engine

def load_model_data():
    """
    Load the model-ready monthly dataset from SQLite.

    Returns
    -------
    pd.DataFrame
        Columns:
        - month
        - avg_hourly_earnings
        - employment_total
        - job_openings
        - unemployment_rate
    """
    engine = get_engine()

    query = """
    SELECT
        month,
        avg_hourly_earnings,
        employment_total,
        job_openings,
        unemployment_rate
    FROM model_monthly
    ORDER BY month;
    """

    df = pd.read_sql(query, engine)
    df["month"] = pd.to_datetime(df["month"]).dt.to_period("M")

    return df


if __name__ == "__main__":
    df = load_model_data()

    print("First 5 rows:")
    print(df.head())

    print("\nShape:", df.shape)

    print("\nDate range:")
    print(df["month"].min(), "→", df["month"].max())

    print("\nSummary statistics:")
    print(df.describe())