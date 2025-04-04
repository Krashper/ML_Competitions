import pandas as pd
from sqlalchemy import create_engine
from dotenv import dotenv_values
import json


def get_conn(dbname, user, password, host):
    url = f"postgresql+psycopg2://{user}:{password}@{host}/{dbname}"
    return create_engine(url)

def save_metrics_to_db():
    config = dotenv_values(".env")
    dbname = config.get('dbname') # Название базы данных
    user = config.get('user') # Имя пользователя для подключения
    password = config.get('password') # Пароль пользователя для подключения
    host = config.get('host') # Хост

    conn = get_conn(dbname, user, password, host)


    with open('dags/results/reg_results.json', 'r') as f:
        data = json.load(f)

    data = pd.DataFrame([data])

    data.to_sql("model_results", conn, index=False, if_exists="append")