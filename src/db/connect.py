import os
#reads env file
from dotenv import load_dotenv
#database connection object
from sqlalchemy import create_engine

load_dotenv()

def get_engine():
    #tries to read DB_PATH from enviornment and if it does not exist then it uses jobmarket.db
    db_path = os.getenv("DB_PATH", "src/db/jobmarket.db")
    return create_engine(f"sqlite:///{db_path}",future= True)

