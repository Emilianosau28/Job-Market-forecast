import pandas as pd 
from xgboost import XGBRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
from src.etl.Loading_modelData import load_model_data
from src.features.feature_builder import build_features

target = "unemployment_rate"

if __name__ == "__main__":

    df  = load_model_data()
    df["month"] = pd.to_datetime(df["month"].astype(str))
    df = df.sort_values("month").reset_index(drop= True)

    df["t"] = range(len(df))

    df_feat = build_features(df)


    features = []

    for i in df_feat.columns:
        if i.startswith("unemployment_rate_lag_") or i.startswith("unemployment_rate_rolling_average_"):
            features.append(i)
    features.append("t")

    df2= df_feat.dropna(subset=features + [target]).copy()
    x = df2[features]
    y = df2[target]

    #split the data
    split = TimeSeriesSplit(n_splits= 5)
    
    fold  = 1
    for train, test in split.split(x):
        xtrain,xtest = x.iloc[train], x.iloc[test]
        ytrain,ytest = y.iloc[train],y.iloc[test]

        model = XGBRegressor(n_estimators =300 ,max_depth = 5, learning_rate = 0.01)

        model.fit(xtrain,ytrain)
        predictions = model.predict(xtest)

        mse = mean_squared_error(ytest,predictions)

        print(f"at fold {fold} mse was: {mse}")

        fold += 1