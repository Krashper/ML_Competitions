import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine
from datetime import date
from typing import Tuple
from dotenv import dotenv_values



st.set_page_config(
    page_title="Water Pollution Desease Dashboard",
    layout="wide"
)

st.title("Дашборд: Болезни из-за загрязнения воды")

def get_conn(dbname, user, password, host):
    url = f"postgresql+psycopg2://{user}:{password}@{host}/{dbname}"
    return create_engine(url)

config = dotenv_values(".env")
dbname = config.get('dbname') # Название базы данных
user = config.get('user') # Имя пользователя для подключения
password = config.get('password') # Пароль пользователя для подключения
host = config.get('host') # Хост


conn = get_conn(dbname, user, password, host)


# Загрузка данных
@st.cache_data
def load_data():

    df = pd.read_sql("SELECT * FROM water_pollution", con=conn)

    return df

# # Функция для фильтрации
def load_data_with_filters(years: Tuple, country: str, water_type: str):
    query = "SELECT * FROM water_pollution WHERE true"

    if years:
        query += f" AND \"Year\" BETWEEN {years[0]} AND {years[1]}"

    if country and country != "Все":
        query += f" AND \"Country\" = '{country}'"

    if water_type and water_type != "Все":
        query += f" AND \"Water Source Type\" = '{water_type}'"
    
    data = pd.read_sql(query, con=conn)

    return data

# Функции для метрик
def load_mean_metrics_by_country(years: Tuple, country: str, water_type: str):
    query = '''
    SELECT "Country",
    AVG("Access to Clean Water (percent of Population)") AS "Mean access to clean water",
    AVG("Diarrheal Cases per 100,000 people") AS "Mean Diarrheal Cases",
    AVG("Cholera Cases per 100,000 people") AS "Mean Cholera Cases",
    AVG("Typhoid Cases per 100,000 people") AS "Mean Typhoid Cases"
    FROM water_pollution
    WHERE true'''

    if years:
        query += f" AND \"Year\" BETWEEN {years[0]} AND {years[1]}"

    if country and country != "Все":
        query += f" AND \"Country\" = '{country}'"

    if water_type and water_type != "Все":
        query += f" AND \"Water Source Type\" = '{water_type}'"
    
    query += ' GROUP BY "Country";'

    data = pd.read_sql(query, con=conn)

    return data

df = load_data()

# Фильтры
start_year, end_year = st.slider(
    "Диапазон лет",
    value=(min(df["Year"]), max(df["Year"])),
    step=1,
    min_value=min(df["Year"])
)

all_countries = np.insert(np.unique(df["Country"].astype(str)), 0, "Все")

selected_country = st.selectbox("Выберите страну:", all_countries)

all_water_types = np.insert(np.unique(df["Water Source Type"].astype(str)), 0, "Все")

selected_water_type = st.selectbox("Выберите тип источника воды:", all_water_types)


selected_years = (start_year, end_year)
filtered_df = load_data_with_filters(selected_years, selected_country, selected_water_type)

data_by_country = load_mean_metrics_by_country(selected_years, selected_country, selected_water_type)


# Построение дашборда
placeholder = st.empty()

with placeholder.container():
    # Таблица
    st.markdown("### Первая 1000 элементов")
    st.dataframe(filtered_df[:min(1000, len(df))])

    # Метрики
    st.markdown("#### Метрики")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Средний уровень загрязняющих веществ",
                round(filtered_df["Contaminant Level (ppm)"].mean(), 2))
    
    col2.metric("Средний уровень pH",
                round(filtered_df["pH Level"].mean(), 2))
    
    col3.metric("Среднее кол-во бактерий",
                round(filtered_df["Bacteria Count (CFU/mL)"].mean(), 2))
    
    col4.metric("Среднее кол-во растворённого кислорода",
                round(filtered_df["Dissolved Oxygen (mg/L)"].mean(), 2))
    

    st.markdown("### Доступность к чистой воде по странам")
    fig = px.histogram(data_by_country, x="Country", y="Mean access to clean water")
    st.write(fig)

    st.markdown("### Заболиваемость диареей (на 100 000 чел) по странам")
    fig = px.histogram(data_by_country, x="Country", y="Mean Diarrheal Cases")
    st.write(fig)

    st.markdown("### Заболиваемость холерой (на 100 000 чел) по странам")
    fig = px.histogram(data_by_country, x="Country", y="Mean Cholera Cases")
    st.write(fig)

    st.markdown("### Заболиваемость тифом (на 100 000 чел) по странам")
    fig = px.histogram(data_by_country, x="Country", y="Mean Typhoid Cases")
    st.write(fig)

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

    