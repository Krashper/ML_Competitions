import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score
import json
import pickle
from dotenv import dotenv_values



def get_conn(dbname, user, password, host):
    url = f"postgresql+psycopg2://{user}:{password}@{host}/{dbname}"
    return create_engine(url)

def get_encoded_data(data):
    cat_cols = ["Gender"] # Категориальные признаки

    encoder = pickle.load(open("dags/models/Encoder.sav", "rb"))
    encoded_data = encoder.transform(data[cat_cols])

    # Получаем имена новых колонок
    feature_names = encoder.get_feature_names_out(cat_cols)

    # Создаем DataFrame с закодированными данными
    data_encoded = pd.DataFrame(encoded_data, columns=feature_names)

    # Объединяем с числовыми колонками
    data = pd.concat([data.drop(cat_cols, axis=1), data_encoded], axis=1)
    return data

def get_scaled_data(data):
    scaler = pickle.load(open("dags/models/Scaler.sav", "rb"))
    scaled_data = scaler.transform(data)

    return scaled_data

def save_metrics_to_json(y_pred, y_true):
    rmse = root_mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    with open("dags/results/reg_results.json", "w") as f:
        reg_results = {
            "rmse": rmse,
            "mae": mae,
            "r2": r2
        }

        json.dump(reg_results, f)

def retrain_model():
    config = dotenv_values(".env")
    dbname = config.get('dbname') # Название базы данных
    user = config.get('user') # Имя пользователя для подключения
    password = config.get('password') # Пароль пользователя для подключения
    host = config.get('host') # Хост

    conn = get_conn(dbname, user, password, host)

    data = pd.read_sql("SELECT * FROM mall_customers;", conn)
    data = data.rename(columns={
        "customerid": "CustomerID", "gender": "Gender",
        "age": "Age"})
    
    data = get_encoded_data(data)
    data = data.drop(columns=["CustomerID"])

    X = data.drop(columns=["Spending Score (1-100)"])
    Y = data["Spending Score (1-100)"]

    X_scaled = get_scaled_data(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, Y, test_size=0.2, random_state=42)
        
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    pickle.dump(lr, open("dags/models/Regression_Model.sav", 'wb'))

    y_pred = lr.predict(X_test)

    save_metrics_to_json(y_pred, y_test)


if __name__ == "__main__":
    retrain_model()