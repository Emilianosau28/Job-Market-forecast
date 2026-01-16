import pandas as pd
from src.etl.Loading_modelData import load_model_data

columnsTo_target = ["avg_hourly_earnings", "employment_total", "job_openings", "unemployment_rate"]

def lag_features(df, lags =(1,6,12)):
    df = df.sort_values("month").copy()
    for columns in columnsTo_target:
        for lag in lags:
            df[f"{columns}_lag_{lag}"] = df[columns].shift(lag)
    
    return df

def rolling_features(df, time_frame = (3,6)):
    df = df.sort_values("month").copy()
    for columns in columnsTo_target:
        for t in time_frame:
            df[f"{columns}_rolling_average_{t}_months"] = (
    df[columns].shift(1).rolling(window=t, min_periods=t).mean()
)
    return df

def build_features(df: pd.DataFrame):
    df_new = lag_features(df, lags=(1, 6, 12))
    df_new = rolling_features(df_new, time_frame=(3, 6))
    return df_new




if __name__ == "__main__":
    df = load_model_data()
    df = df.sort_values("month")
    df_new = build_features(df)

    print(df_new.head(15))
