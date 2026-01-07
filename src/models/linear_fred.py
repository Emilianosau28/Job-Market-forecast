import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
from src.etl.Loading_modelData import load_model_data
from src.features.feature_builder import build_features


data = load_model_data()
data = build_features(data)

data = data.dropna().sort_values("month").reset_index(drop= True)

target_column = "avg_hourly_earnings"

features = [c for c in data.columns if c not in ["month", target_column]]

x = data[features]
y = data[target_column]

split = TimeSeriesSplit(n_splits= 5)

fold = 0
for train_idx, test_idx in split.split(x):
    x_train , x_test = x.iloc[train_idx], x.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    model = LinearRegression()
    model.fit(x_train,y_train)
    
    pred = model.predict(x_test)
    mse = mean_squared_error(y_test,pred)
    fold += 1

    print(f"at fold {fold} MSE was: {mse}")

