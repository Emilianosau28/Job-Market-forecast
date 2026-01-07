import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

from src.etl.Loading_modelData import load_model_data
from src.features.feature_builder import build_features


if __name__ == "__main__":
    df = load_model_data()

    df_feat = build_features(df)

    df_feat = df_feat.dropna().sort_values("month").reset_index(drop=True)

    tscross_validation = TimeSeriesSplit(n_splits=5)

    for fold, (train_idx, test_idx) in enumerate(tscross_validation.split(df_feat), start=1):
        train = df_feat.iloc[train_idx]
        test = df_feat.iloc[test_idx]

