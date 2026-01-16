import pandas as pd
import numpy as np
from xgboost import XGBRegressor

from src.etl.Loading_modelData import load_model_data
from src.features.feature_builder import build_features
from src.db.connect import get_engine

TARGET = "unemployment_rate"
HORIZON = 60  # months


def make_feature_list(df_feat: pd.DataFrame) -> list:
    feats = []
    for c in df_feat.columns:
        if c.startswith(f"{TARGET}_lag_") or c.startswith(f"{TARGET}_rolling_average_"):
            feats.append(c)
    feats.append("t")
    return feats


if __name__ == "__main__":
    # 1) Load data
    df = load_model_data()
    df["month"] = pd.to_datetime(df["month"].astype(str))
    df = df.sort_values("month").reset_index(drop=True)

    # 2) IMPORTANT: remove any rows where TARGET is missing
    # This prevents rolling windows from becoming NaN at the end of history
    df = df[df[TARGET].notna()].copy()
    df = df.sort_values("month").reset_index(drop=True)

    # 3) Add time index
    df["t"] = range(len(df))

    # 4) Build features
    df_feat = build_features(df)

    features = make_feature_list(df_feat)

    # 5) Train data (must have all features + target)
    train = df_feat.dropna(subset=features + [TARGET]).copy()
    X_train = train[features]
    y_train = train[TARGET]

    model = XGBRegressor(
        n_estimators=400,
        max_depth=4,
        learning_rate=0.01,
        subsample=1.0,
        colsample_bytree=1.0,
        random_state=42,
    )
    model.fit(X_train, y_train)

    # 6) Recursive forecast loop
    df_roll = df.copy()
    forecasts = []

    for step in range(HORIZON):
        next_month = df_roll["month"].max() + pd.offsets.MonthBegin(1)

        # append a new empty row for next month
        new_row = {col: np.nan for col in df_roll.columns}
        new_row["month"] = next_month
        new_row["t"] = int(df_roll["t"].max()) + 1

        df_roll = pd.concat([df_roll, pd.DataFrame([new_row])], ignore_index=True)

        # rebuild features using df_roll
        df_roll_feat = build_features(df_roll)
        last_row = df_roll_feat.iloc[-1]
        X_next = last_row[features].to_frame().T

        # if we still can't compute features, stop
        if X_next.isna().any().any():
            missing = X_next.columns[X_next.isna().iloc[0]].tolist()
            print("NaNs found in nextX (cannot predict). Missing:", missing)
            break

        pred = float(model.predict(X_next)[0])

        # write prediction back into the rolling dataframe
        df_roll.loc[df_roll.index[-1], TARGET] = pred

        forecasts.append({"month": next_month, TARGET: pred})

    forecast_df = pd.DataFrame(forecasts)

    print("\nForecast preview:")
    print(forecast_df.head())

    print("\nForecast tail:")
    print(forecast_df.tail())

    print("\nRows:", len(forecast_df))

    # 7) Save only if we actually forecasted something
    if forecast_df.empty:
        print("\nNo forecasts generated -> not saving to SQLite.")
        raise SystemExit(0)

    engine = get_engine()
    forecast_df.to_sql(
        "forecast_unemployment_rate_xgb",
        engine,
        if_exists="replace",
        index=False
    )
    print("\nSaved to SQLite table: forecast_unemployment_rate_xgb")



