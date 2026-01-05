import pandas as pd
from sklearn.linear_model import LinearRegression
from src.etl.pullingData import Load_monthly_Job_postings as Lmjp

def Create_time_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["month"] = pd.to_datetime(df["month"])
    df = df.sort_values("month")
    df["t"] = range(len(df))
    return df

if __name__ == "__main__":
    df = Lmjp()

    df = df[(df["region"] == "US") & (df["job_category"] == "Data Science")]
    df = Create_time_index(df)
    
    x = [["t"]]
    y = df["postings_count"]


    model = LinearRegression()
    model.fit(x,y)

    t_plus1 = [[df["t"].max() + 1]]

    nextPred = model.predict(t_plus1)[0]
    