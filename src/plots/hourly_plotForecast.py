import pandas as pd
import matplotlib.pyplot as plt

from src.etl.Loading_modelData import load_model_data
from src.db.connect import get_engine


if __name__ == "__main__":

    hist = load_model_data()
    hist["month"] = pd.to_datetime(hist["month"].astype(str))

    engine = get_engine()
    forecast = pd.read_sql(
        "SELECT * FROM forecast_hourly_earnings_monthly",
        engine
    )
    forecast["month"] = pd.to_datetime(forecast["month"])

    plt.figure(figsize=(12, 6))

    plt.plot(
        hist["month"],
        hist["avg_hourly_earnings"],
        label="Historical",
        linewidth=2,
        color ="black"
    )

    plt.plot(
        forecast["month"],
        forecast["avg_hourly_earnings"],
        label="Forecast",
        linestyle="--",
        linewidth=2
    )

    plt.xlabel("Year")
    plt.ylabel("Average Hourly Earnings ($)")
    plt.title("Average Hourly Earnings Forecast")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()
