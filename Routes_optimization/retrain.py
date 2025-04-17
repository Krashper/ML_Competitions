import streamlit as st
import pandas as pd
import pickle
import sqlite3
import time
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import StratifiedKFold
from imblearn.over_sampling import SMOTE


def get_encoded_data(data):
    ohe_season = pickle.load(open("Encoder_1.sav", "rb"))
    seasons = ohe_season.fit_transform(data[['season']])
    seasons_df = pd.DataFrame(seasons.toarray(), columns=ohe_season.get_feature_names_out())
    data = pd.concat([data.drop(['season'], axis=1), seasons_df], axis=1)
    return data

def get_scaled_data(data):
    scaler = pickle.load(open("Scaler_1.sav", "rb"))
    return scaler.transform(data)

def get_smote_data(X, y):
    smote = SMOTE()
    return smote.fit_resample(X, y)

def train_cross_val_model(X_scaled, y, model):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    all_metrics = []

    for train_idx, test_idx in skf.split(X_scaled, y):
        X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        X_train, y_train = get_smote_data(X_train, y_train)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        fold_metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision_macro": precision_score(y_test, y_pred, average='macro', zero_division=0),
            "recall_macro": recall_score(y_test, y_pred, average='macro', zero_division=0),
            "f1_macro": f1_score(y_test, y_pred, average='macro'),
            "f1_weighted": f1_score(y_test, y_pred, average='weighted'),
        }

        all_metrics.append(fold_metrics)

    return model, pd.DataFrame(all_metrics).mean().to_dict()

def save_metrics_to_db(metrics, model_name):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metrics["timestamp"] = [now]
    metrics["model_name"] = [model_name]
    df = pd.DataFrame(metrics)
    conn = sqlite3.connect("database.db")
    try:
        df.to_sql("model_metrics", conn, if_exists="append", index=False)
    except Exception as e:
        print("Ошибка при сохранении:", e)

# Streamlit UI

st.title("🔁 Непрерывное обучение модели")
start = st.button("Начать обучать")
stop = st.button("Остановить")

# Время задержки между циклами (секунды)
interval = st.number_input("⏱ Задержка между циклами (сек):", value=900, step=60)

if start:
    st.success("Запущено обучение")

    # Бесконечный цикл
    while True:
        try:
            # Загружаем данные
            # conn = sqlite3.connect("database.db")
            # query = "SELECT * FROM final_dataset"
            # data = pd.read_sql(query, conn)

            data = pd.read_csv("final_dataset.csv").drop(columns=["Unnamed: 0", "Unnamed: 0.1"])

            if data.empty:
                st.warning("Нет данных для обучения.")
                time.sleep(interval)
                continue

            X = data.drop(columns=["water_and_fire_cluster", "track_id", "DateTime", "region"])
            y = data["water_and_fire_cluster"]
            X_encoded = get_encoded_data(X)
            X_scaled = get_scaled_data(X_encoded)

            model = LogisticRegression(random_state=42)
            model, metrics = train_cross_val_model(X_scaled, y, model)

            # Сохраняем модель и метрики
            pickle.dump(model, open("Classification_Model_1.sav", 'wb'))
            save_metrics_to_db(metrics, "Water_Fire_Model")

            st.write(f"Модель обучена: {datetime.now().strftime('%H:%M:%S')}")
            st.json(metrics)

        except Exception as e:
            st.error(f"Ошибка: {e}")

        time.sleep(interval)

elif stop:
    st.warning("Остановка цикла обучения (перезапустите Streamlit вручную)")
