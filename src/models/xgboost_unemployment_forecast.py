import pandas as pd
from xgboost import XGBRegressor
import numpy as np

from src.etl.Loading_modelData import load_model_data
from src.features.feature_builder import build_features
from src.db.connect import get_engine

target = "unemployment_rate"
horizon = 60


def get_featureCols(df, target: str):
    df = pd.DataFrame(df)
    features = []
    for i in df.columns:
        if i.startswith(f"{target}_lag_") or i.startswith(f"{target}_rolling_average_"):
            features.append(i)

    features.append("t")
    return features


if __name__ == "__main__":
    df = load_model_data()

    df["month"] = pd.to_datetime(df["month"].astype(str), errors="coerce")
    df = df.dropna(subset=["month"]).copy()


    df["month"] = df["month"].values.astype("datetime64[M]")
    df["month"] = pd.to_datetime(df["month"])


    df = df.sort_values("month").set_index("month").asfreq("MS")

    
    df[target] = pd.to_numeric(df[target], errors="coerce")
    df[target] = df[target].interpolate(method="time").ffill().bfill()


    df = df.reset_index()
    df = df.sort_values("month").reset_index(drop=True)

    df["t"] = range(len(df))


    df_feat = build_features(df)
    featureCols = get_featureCols(df_feat, target)


    df_feat["target_next"] = pd.to_numeric(df_feat[target], errors="coerce").shift(-1)
    df_feat["delta_target"] = df_feat["target_next"] - pd.to_numeric(df_feat[target], errors="coerce")

    train = df_feat.dropna(subset=featureCols + [target, "delta_target"]).copy()

    xtrain = (
        train[featureCols]
        .apply(pd.to_numeric, errors="coerce")
        .astype(float)
    )
    ytrain = pd.to_numeric(train["delta_target"], errors="coerce").astype(float)

    mask = xtrain.notna().all(axis=1) & ytrain.notna()
    xtrain = xtrain.loc[mask]
    ytrain = ytrain.loc[mask]

    model = XGBRegressor(n_estimators=400, max_depth=4, learning_rate=0.01)
    model.fit(xtrain, ytrain)

    dfroll = df.copy()
    forecasts = []

    for j in range(horizon):
        df_roll_feat = build_features(dfroll)
        X_curr = df_roll_feat.loc[df_roll_feat.index[-1], featureCols].to_frame().T
        X_curr = X_curr.apply(pd.to_numeric, errors="coerce").astype(float)

        if X_curr.isna().any().any():
            missing = X_curr.columns[X_curr.isna().iloc[0]].tolist()
            print("Null values found in X_curr (cannot forecast). Missing:", missing)
            break

        curr_level = float(dfroll.loc[dfroll.index[-1], target])
        pred_delta = float(model.predict(X_curr)[0])
        next_level = curr_level + pred_delta

        next_month = dfroll["month"].max() + pd.offsets.MonthBegin(1)
        next_t = int(dfroll["t"].max()) + 1

        new_row = {c: np.nan for c in dfroll.columns}
        new_row.update({"month": next_month, "t": next_t, target: next_level})
        dfroll = pd.concat([dfroll, pd.DataFrame([new_row])], ignore_index=True)

        forecasts.append({"month": next_month, target: next_level})

    forecast_df = pd.DataFrame(forecasts)

    print("\nForecast preview:")
    print(forecast_df.head())
    print("\nForecast tail:")
    print(forecast_df.tail())

    if forecast_df.empty:
        print("not saving to SQLite.")
    else:
        engine = get_engine()
        forecast_df.to_sql(
            "forecast_unemployment_rate_xgb",
            engine,
            if_exists="replace",
            index=False
        )
        print("success sql save")


