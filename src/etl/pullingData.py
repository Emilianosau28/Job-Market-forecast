import pandas as pd
from src.db.connect import get_engine

def Load_monthly_Job_postings():
    engine = get_engine()
    query = """
    SELECT month, region, job_category, postings_count
    FROM job_postings_monthly
    ORDER BY month;
    """
    return pd.read_sql(query, engine)

if __name__ == "__main__":
    df = Load_monthly_Job_postings()
    print(df)