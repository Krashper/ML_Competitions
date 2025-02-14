import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import yaml
from database import DataBase


st.set_page_config(
    page_title="Stations Dashboard",
    layout="wide"
)

st.title("Интерактивный дашборд для станций метро")

with open("sql/db_data.yaml") as file:
    config = yaml.safe_load(file)

conn_data = config["database"]["connection"]
queries = config["database"]["queries"]

@st.cache_data
def load_data():
    db = DataBase(conn_data["username"], conn_data["password"], conn_data["db_name"], conn_data["host"], conn_data["port"])

    df = db.execute_query(queries["get_db_stations"])

    return df

def get_average_passengers_by_date(df: pd.DataFrame):
    average_df = df.groupby("date").agg({
        "num_val": "mean"
    }).reset_index()
    return average_df

def get_passengers_stat(df: pd.DataFrame):
    results = [
        ["Мин. кол-во", df["num_val"].min()],
        ["Среднее кол-во", int(df["num_val"].mean())],
        ["Медианное кол-во", int(df["num_val"].median())],
        ["Макс. кол-во", df["num_val"].max()]
    ]

    result_df = pd.DataFrame(results, columns=["Стат. величина", "Значение"])

    return result_df

df = load_data()

start_date, end_date = st.slider(
    "Диапазон дат",
    value=(df["date"].min(), df["date"].max()),
    format="DD/MM/YY"
)

filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

all_lines = np.insert(np.unique(filtered_df["line_name"]), 0, "Все")

line_filter = st.selectbox("Выберите линию", all_lines)

if line_filter != "Все":
    filtered_df = filtered_df[filtered_df["line_name"] == line_filter]

all_stations = np.insert(np.unique(filtered_df["station_name"]), 0, "Все")

station_filter = st.selectbox("Выберите станцию", all_stations)

if station_filter != "Все":
    filtered_df = filtered_df[filtered_df["station_name"] == station_filter]

placeholder = st.empty()

with placeholder.container():
    st.markdown("### Первые 10000 элементов выборки")
    st.dataframe(filtered_df[:min(10000, len(filtered_df))])

    st.markdown("#### Среднее кол-во пассажиров")
    average_df = get_average_passengers_by_date(filtered_df)
    fig = px.line(average_df, x="date", y="num_val", markers=True)
    st.write(fig)

    st.markdown("#### Кол-во пассажиров (статистические значения)")
    stat_df = get_passengers_stat(filtered_df).sort_values(by="Значение", ascending=False)
    fig = px.funnel(stat_df, x="Значение", y="Стат. величина")
    st.write(fig)