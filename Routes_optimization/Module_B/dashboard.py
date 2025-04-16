import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine
from datetime import date
from typing import Tuple
from dotenv import dotenv_values
import sqlite3



st.set_page_config(
    page_title="Аналитический дашборд",
    layout="wide"
)

st.title("Аналитический дашборд")

conn = sqlite3.connect("database.db")


# Загрузка данных
@st.cache_data
def load_data():

    df = pd.read_sql("SELECT * FROM result_data", con=conn)

    return df

# Функция для фильтрации
def load_data_with_filters(track, date_range, season, hour_range):
    query = "SELECT * FROM result_data WHERE true"

    if track and track != "Все":
        query += f" AND track_id = '{track}'"
    if date_range:
        query += f" AND DATE(\"DateTime\") BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
    if season and season != "Все":
        query += f" AND season = '{season}'"
    if hour_range:
        query += f" AND hour BETWEEN {hour_range[0]} AND {hour_range[1]}"
    
    data = pd.read_sql(query, con=conn)

    return data

# Функции для метрик
def get_avg_temp_by_hour(track, date_range, season, hour_range):
    query = "SELECT hour, AVG(temp) AS avg_temp FROM result_data WHERE true"

    if track and track != "Все":
        query += f" AND track_id = '{track}'"
    if date_range:
        query += f" AND DATE(\"DateTime\") BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
    if season and season != "Все":
        query += f" AND season = '{season}'"
    if hour_range:
        query += f" AND hour BETWEEN {hour_range[0]} AND {hour_range[1]}"
    
    query += " GROUP BY hour"

    data = pd.read_sql(query, con=conn)

    return data

# Для заглушки используется temp, а не steps
def get_user_active_by_water_env(track, date_range, season, hour_range):
    query = """SELECT
        CASE
            WHEN water_dist = -1 THEN 'Нет воды рядом'
            WHEN water_dist <= 100 THEN 'Очень близко к воде (<= 100)'
            ELSE 'Близко к воде (101-500)'
        END AS water,
        AVG(temp) AS avg_steps
        FROM result_data
        WHERE true"""

    if track and track != "Все":
        query += f" AND track_id = '{track}'"
    if date_range:
        query += f" AND DATE(\"DateTime\") BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
    if season and season != "Все":
        query += f" AND season = '{season}'"
    if hour_range:
        query += f" AND hour BETWEEN {hour_range[0]} AND {hour_range[1]}"

    query += " GROUP BY water"

    data = pd.read_sql(query, con=conn)

    return data

# Для заглушки используется temp, а не steps
def get_user_active_by_building_env(track, date_range, season, hour_range):
    query = """SELECT
        CASE
            WHEN building_dist = -1 THEN 'Нет зданий рядом'
            WHEN building_dist <= 100 THEN 'Очень близко к зданию (<= 100)'
            ELSE 'Близко к зданию (101-500)'
        END AS building,
        AVG(temp) AS avg_steps
        FROM result_data
        WHERE true"""

    if track and track != "Все":
        query += f" AND track_id = '{track}'"
    if date_range:
        query += f" AND DATE(\"DateTime\") BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
    if season and season != "Все":
        query += f" AND season = '{season}'"
    if hour_range:
        query += f" AND hour BETWEEN {hour_range[0]} AND {hour_range[1]}"

    query += " GROUP BY building"

    data = pd.read_sql(query, con=conn)

    return data

# Для заглушки используется temp, а не steps
def get_user_active_by_green_env(track, date_range, season, hour_range):
    query = """SELECT
        CASE
            WHEN green_dist = -1 THEN 'Нет зелени рядом'
            WHEN green_dist <= 100 THEN 'Очень близко к зелени (<= 100)'
            ELSE 'Близко к зелени (101-500)'
        END AS green,
        AVG(temp) AS avg_steps
        FROM result_data
        WHERE true"""

    if track and track != "Все":
        query += f" AND track_id = '{track}'"
    if date_range:
        query += f" AND DATE(\"DateTime\") BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
    if season and season != "Все":
        query += f" AND season = '{season}'"
    if hour_range:
        query += f" AND hour BETWEEN {hour_range[0]} AND {hour_range[1]}"

    query += " GROUP BY green"

    data = pd.read_sql(query, con=conn)

    return data

# Для заглушки используется temp вместо steps
def get_user_active_by_altitude(track, date_range, season, hour_range):
    query = """SELECT
        track_id,
        AVG(altitude) AS avg_altitude,
        AVG(temp) AS avg_steps
        FROM result_data
        WHERE true"""
    
    if track and track != "Все":
        query += f" AND track_id = '{track}'"
    if date_range:
        query += f" AND DATE(\"DateTime\") BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
    if season and season != "Все":
        query += f" AND season = '{season}'"
    if hour_range:
        query += f" AND hour BETWEEN {hour_range[0]} AND {hour_range[1]}"

    query += " GROUP BY track_id"

    data = pd.read_sql(query, con=conn)

    return data

def get_popular_tracks(track, date_range, season, hour_range):
    sub_query = """SELECT DISTINCT track_id, DATE("DateTime") AS route_day
    FROM result_data
    WHERE true"""
    
    if track and track != "Все":
        sub_query += f" AND track_id = '{track}'"
    if date_range:
        sub_query += f" AND DATE(\"DateTime\") BETWEEN '{date_range[0]}' AND '{date_range[1]}'"
    if season and season != "Все":
        sub_query += f" AND season = '{season}'"
    if hour_range:
        sub_query += f" AND hour BETWEEN {hour_range[0]} AND {hour_range[1]}"

    query = f"""SELECT track_id, COUNT(*) AS routes_count
    FROM ({sub_query})
    GROUP BY track_id
    ORDER BY routes_count DESC"""

    data = pd.read_sql(query, con=conn)

    return data

# Загрузка данных

df = load_data()
df["DateTime"] = pd.to_datetime(df["DateTime"]).dt.date


# Фильтры
all_tracks = np.insert(np.unique(df["track_id"].astype(str)), 0, "Все")

selected_track = st.selectbox("Выберите Трек:", all_tracks)

start_date, end_date = st.slider(
    "Диапазон дат",
    value=(df["DateTime"].min(), df["DateTime"].max())
)
date_range = (start_date, end_date)

all_seasons = np.insert(np.unique(df["season"].astype(str)), 0, "Все")

selected_season = st.selectbox("Выберите Сезон:", all_seasons)

start_hour, end_hour = st.slider(
    "Диапазон часов",
    value=(min(df["hour"]), max(df["hour"])),
    step=1,
    max_value=max(df["hour"])
)
hour_range = (start_hour, end_hour)

filtered_df = load_data_with_filters(selected_track, date_range, selected_season, hour_range)

# start_battery_power, end_battery_power = st.slider(
#     "Диапазон мощьности батареи",
#     value=(min(df["battery_power"]), max(df["battery_power"])),
#     step=1
# )

# # Изменения данных на основе фильтров
# battery_power = (start_battery_power, end_battery_power)
# filtered_df = load_data_with_filters(battery_power, selected_price_range)

# Построение дашборда
placeholder = st.empty()

with placeholder.container():
    # Таблица
    st.markdown("### Первые 10000 элементов")
    st.dataframe(filtered_df[:min(10000, len(filtered_df))])
    
    st.markdown("### Температура воздуха относительно времени суток")
    fig = px.bar(get_avg_temp_by_hour(selected_track, date_range, selected_season, hour_range), x="hour", y="avg_temp")
    fig.update_layout(bargap=0.2)
    st.write(fig)

    st.markdown("### Активность пользователя относительно окружающей среды (вода)")
    fig = px.bar(get_user_active_by_water_env(selected_track, date_range, selected_season, hour_range), y="water", x="avg_steps")
    fig.update_layout(bargap=0.2)
    st.write(fig)

    st.markdown("### Активность пользователя относительно окружающей среды (здания)")
    fig = px.bar(get_user_active_by_building_env(selected_track, date_range, selected_season, hour_range), y="building", x="avg_steps")
    fig.update_layout(bargap=0.2)
    st.write(fig)

    st.markdown("### Активность пользователя относительно окружающей среды (зелень)")
    fig = px.bar(get_user_active_by_green_env(selected_track, date_range, selected_season, hour_range), y="green", x="avg_steps")
    fig.update_layout(bargap=0.2)
    st.write(fig)

    st.markdown("### Активность пользователя относительно средней высоты для каждого трека")
    fig = px.bar(get_user_active_by_altitude(selected_track, date_range, selected_season, hour_range), x="avg_altitude", y="avg_steps", hover_data=['track_id'], hovermode="y")
    fig.update_layout(bargap=0.2)
    st.write(fig)

    st.markdown("### Популярность треков")
    st.dataframe(get_popular_tracks(selected_track, date_range, selected_season, hour_range))
    # # Метрики
    # st.markdown("#### Метрики")
    # col1, col2 = st.columns(2)
    # col1.metric("Отношение средней длины к ширине",
    #             round(get_height_width_coef(battery_power, selected_price_range), 2))
    
    # col2.metric("Заглушка", 2)

    # # Гистрограмма по 1 переменной
    # st.markdown("### Распределение телефонов по наличию Bluetooth")
    # fig = px.histogram(filtered_df, x="blue")
    # fig.update_layout(bargap=0.2)
    # st.write(fig)

    # # Гистрограмма по 2 переменным
    # st.markdown("### Распределение времени отклика ЦП, относительно Price Range")
    # fig = px.histogram(filtered_df, x="price_range", y="clock_speed", histfunc="avg")
    # fig.update_layout(bargap=0.2)
    # st.write(fig)

    # # Бокс плот
    # st.markdown("### Boxplot: Распределение памяти по Price Range")
    # fig = px.box(filtered_df, x="price_range", y="ram")
    # st.write(fig)

    # # Скаттер плот
    # st.markdown("### Scatter Plot: RAM vs Battery Power")
    # fig = px.scatter(filtered_df, x="ram", y="battery_power", color="wifi")
    # st.write(fig)

    # # Линейный график
    # st.markdown("### Линейный график (пример: по порядку индекса)")
    # fig = px.line(filtered_df.reset_index(), x=filtered_df.index, y="battery_power")
    # st.write(fig)

    # # Heatmap
    # st.markdown("### Тепловая карта корреляции")
    # corr = filtered_df.select_dtypes(include=np.number).corr()
    # fig = px.imshow(corr, text_auto=True, aspect="auto", title="Корреляция признаков")
    # st.write(fig)

    # # Круговая диаграмма
    # st.markdown("### Pie Chart: Доля по Price Range")
    # pie_df = filtered_df["price_range"].value_counts().reset_index()
    # pie_df.columns = ["price_range", "count"]
    # fig = px.pie(pie_df, names="price_range", values="count")
    # st.write(fig)

    # # Гистограмма с доп графиком
    # st.markdown("### Histogram: Плотность Battery Power")
    # fig = px.histogram(filtered_df, x="battery_power", marginal="rug", nbins=30)
    # st.write(fig)

    