import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine
from datetime import date
from typing import Tuple
from dotenv import dotenv_values



st.set_page_config(
    page_title="Dashboard Template",
    layout="wide"
)

st.title("Dashboard Template")

def get_conn(dbname, user, password, host, port):
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    return create_engine(url)

config = dotenv_values(".env")
dbname = config.get('dbname') # Название базы данных
user = config.get('user') # Имя пользователя для подключения
password = config.get('password') # Пароль пользователя для подключения
host = config.get('host') # Хост
port = config.get('port') # Порт


conn = get_conn(dbname, user, password, host, port)


# Загрузка данных
@st.cache_data
def load_data():

    df = pd.read_sql("SELECT * FROM template_table", con=conn)

    return df

# Функция для фильтрации
def load_data_with_filters(battery_power: Tuple, price_range: int):
    query = "SELECT * FROM template_table WHERE true"

    if battery_power:
        query += f" AND battery_power BETWEEN {battery_power[0]} AND {battery_power[1]}"

    if price_range and price_range != "Все":
        query += f" AND price_range = {price_range}"
    
    data = pd.read_sql(query, con=conn)

    return data

# Функции для метрик
def get_height_width_coef(battery_power: Tuple, price_range: int):
    query = """SELECT (AVG(px_height) / AVG(px_width)) AS coef FROM template_table
    WHERE true"""

    if battery_power:
        query += f" AND battery_power BETWEEN {battery_power[0]} AND {battery_power[1]}"

    if price_range and price_range != "Все":
        query += f" AND price_range = {price_range}"
    
    data = pd.read_sql(query, con=conn)["coef"][0]

    return data

# Загрузка данных

df = load_data()


# Фильтры
# start_date, end_date = st.slider(
#     "Диапазон дат",
#     value=(df["date"].min(), df["date"].max()),
#     format="YY-MM-DD"
# )

start_battery_power, end_battery_power = st.slider(
    "Диапазон мощьности батареи",
    value=(min(df["battery_power"]), max(df["battery_power"])),
    step=1
)

all_price_ranges = np.insert(np.unique(df["price_range"].astype(str)), 0, "Все")

selected_price_range = st.selectbox("Выберите Price Range:", all_price_ranges)

# Изменения данных на основе фильтров
battery_power = (start_battery_power, end_battery_power)
filtered_df = load_data_with_filters(battery_power, selected_price_range)

# Построение дашборда
placeholder = st.empty()

with placeholder.container():
    # Таблица
    st.markdown("### Первые 10000 элементов")
    st.dataframe(filtered_df[:min(10000, len(filtered_df))])

    # Метрики
    st.markdown("#### Метрики")
    col1, col2 = st.columns(2)
    col1.metric("Отношение средней длины к ширине",
                round(get_height_width_coef(battery_power, selected_price_range), 2))
    
    col2.metric("Заглушка", 2)

    # Гистрограмма по 1 переменной
    st.markdown("### Распределение телефонов по наличию Bluetooth")
    fig = px.histogram(filtered_df, x="blue")
    fig.update_layout(bargap=0.2)
    st.write(fig)

    # Гистрограмма по 2 переменным
    st.markdown("### Распределение времени отклика ЦП, относительно Price Range")
    fig = px.histogram(filtered_df, x="price_range", y="clock_speed", histfunc="avg")
    fig.update_layout(bargap=0.2)
    st.write(fig)

    # Бокс плот
    st.markdown("### Boxplot: Распределение памяти по Price Range")
    fig = px.box(filtered_df, x="price_range", y="ram")
    st.write(fig)

    # Скаттер плот
    st.markdown("### Scatter Plot: RAM vs Battery Power")
    fig = px.scatter(filtered_df, x="ram", y="battery_power", color="wifi")
    st.write(fig)

    # Линейный график
    st.markdown("### Линейный график (пример: по порядку индекса)")
    fig = px.line(filtered_df.reset_index(), x=filtered_df.index, y="battery_power")
    st.write(fig)

    # Heatmap
    st.markdown("### Тепловая карта корреляции")
    corr = filtered_df.select_dtypes(include=np.number).corr()
    fig = px.imshow(corr, text_auto=True, aspect="auto", title="Корреляция признаков")
    st.write(fig)

    # Круговая диаграмма
    st.markdown("### Pie Chart: Доля по Price Range")
    pie_df = filtered_df["price_range"].value_counts().reset_index()
    pie_df.columns = ["price_range", "count"]
    fig = px.pie(pie_df, names="price_range", values="count")
    st.write(fig)

    # Гистограмма с доп графиком
    st.markdown("### Histogram: Плотность Battery Power")
    fig = px.histogram(filtered_df, x="battery_power", marginal="rug", nbins=30)
    st.write(fig)

    
