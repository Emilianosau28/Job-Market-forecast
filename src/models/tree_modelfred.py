import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor

from src.etl.Loading_modelData import load_model_data
from src.features.feature_builder import build_features


def TreePrediction(target, splits =5):
    df = load_model_data()
    df = build_features(df)
    df = df.dropna().sort_values("month").reset_index(drop=True)


    features = df.select_dtypes(include="number").columns.tolist()
    features.remove(target)

    x = df[features]
    y = df[target]

    timeSeriesCrossVal = TimeSeriesSplit(n_splits=splits)
    fold = 0
    for train_idx, test_idx in timeSeriesCrossVal.split(x):
        xtrain, xtest = x.iloc[train_idx], x.iloc[test_idx]
        ytrain,ytest = y.iloc[train_idx],y.iloc[test_idx]

        model = RandomForestRegressor(n_estimators=500)
        model.fit(xtrain,ytrain)
        predictions = model.predict(xtest)

        mse = mean_squared_error(ytest,predictions)
        fold +=1
        print(f"at fold {fold} MSE was: {mse}")


if __name__ == "__main__":
    
    TreePrediction("avg_hourly_earnings")

    print("\n" + "-" * 60 + "\n")

    TreePrediction("unemployment_rate")