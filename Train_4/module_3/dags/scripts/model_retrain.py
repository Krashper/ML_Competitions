import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, r2_score
import json
import pickle
from dotenv import dotenv_values



def get_conn(dbname, user, password, host):
    url = f"postgresql+psycopg2://{user}:{password}@{host}/{dbname}"
    return create_engine(url)

def get_encoded_data(data):
    cat = ["object"]

    cat_data = data.select_dtypes(include=cat)

    cat_cols = cat_data.columns # Категориальные признаки

    encoder = pickle.load(open("models/Encoder.sav", "rb"))
    encoded_data = encoder.transform(data[cat_cols])

    # Получаем имена новых колонок
    feature_names = encoder.get_feature_names_out(cat_cols)

    # Создаем DataFrame с закодированными данными
    data_encoded = pd.DataFrame(encoded_data, columns=feature_names)

    # Объединяем с числовыми колонками
    data = pd.concat([data.drop(cat_cols, axis=1), data_encoded], axis=1)
    return data

def get_scaled_data(data):
    scaler = pickle.load(open("models/Scaler.sav", "rb"))
    scaled_data = scaler.transform(data)

    scaled_data = pd.DataFrame(scaled_data, columns=data.columns)

    return scaled_data

def get_pca_data(data):
    pca = pickle.load(open("models/PCA.sav", "rb"))
    pca_data = pca.transform(data)

    return pca_data

def save_metrics_to_json(y_pred, y_true):
    rmse = root_mean_squared_error(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    with open("results/reg_results.json", "w") as f:
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

    data = pd.read_sql("SELECT * FROM water_pollution;", conn)
    data = data.rename(columns={"Access to Clean Water (percent of Population)": "Access to Clean Water (% of Population)"})
    
    data = get_encoded_data(data)

    X = data.drop("Population Density (people per km²)", axis=1)
    Y = data["Population Density (people per km²)"]

    X_scaled = get_scaled_data(X)
    X_pca = get_pca_data(X_scaled)

    X_train, X_test, y_train, y_test = train_test_split(
        X_pca, Y, test_size=0.2, random_state=42)
        
    gb = GradientBoostingRegressor()
    gb.fit(X_train, y_train)
    pickle.dump(gb, open("models/GradientBoostingRegressor.sav", 'wb'))

    y_pred = gb.predict(X_test)

    save_metrics_to_json(y_pred, y_test)


if __name__ == "__main__":
    retrain_model()