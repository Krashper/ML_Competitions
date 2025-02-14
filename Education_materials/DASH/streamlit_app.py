import yaml
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Заголовок приложения
st.title("Анализ выживаемости пассажиров Титаника 🚢")

# Подключение к базе данных
conn = sqlite3.connect('titanic.db')

# Загрузка данных из базы данных
@st.cache_data  # Кэширование для ускорения загрузки
def load_data():
    query = '''
    SELECT p.PassengerId, p.Name, p.Sex, p.Age, p.Survived, p.Pclass, t.Fare, t.Cabin, t.Embarked
    FROM Passengers p
    JOIN PassengerTickets pt ON p.PassengerId = pt.PassengerId
    JOIN Tickets t ON pt.TicketId = t.TicketId
    '''
    return pd.read_sql(query, conn)

# Загрузка данных
df = load_data()

# Отображение данных
st.write("### Данные пассажиров Титаника")
st.dataframe(df)

# Фильтры для анализа
st.sidebar.header("Фильтры")

# Фильтр по полу
sex_filter = st.sidebar.selectbox("Выберите пол", ["Все", "Мужской", "Женский"])

# Фильтр по классу билета
pclass_filter = st.sidebar.selectbox("Выберите класс", ["Все", "1", "2", "3"])

# Фильтр по возрасту
age_filter = st.sidebar.slider("Выберите возраст", min_value=0, max_value=100, value=(0, 100))

# Применение фильтров
filtered_df = df.copy()
if sex_filter != "Все":
    filtered_df = filtered_df[filtered_df["Sex"] == ("male" if sex_filter == "Мужской" else "female")]
if pclass_filter != "Все":
    filtered_df = filtered_df[filtered_df["Pclass"] == int(pclass_filter)]
filtered_df = filtered_df[(filtered_df["Age"] >= age_filter[0]) & (filtered_df["Age"] <= age_filter[1])]

# Отображение отфильтрованных данных
st.write("### Отфильтрованные данные")
st.dataframe(filtered_df)

# Визуализация выживаемости
st.write("### Анализ выживаемости")

# Круговая диаграмма выживаемости
survived_counts = filtered_df["Survived"].value_counts().rename({0: "Погиб", 1: "Выжил"})
fig_pie = px.pie(
    survived_counts,
    values=survived_counts.values,
    names=survived_counts.index,
    title="Соотношение выживших и погибших"
)
st.plotly_chart(fig_pie)

# Гистограмма выживаемости по полу
fig_sex = px.histogram(
    filtered_df,
    x="Sex",
    color="Survived",
    barmode="group",
    title="Выживаемость по полу",
    labels={"Sex": "Пол", "count": "Количество"},
    color_discrete_map={0: "red", 1: "green"}
)
st.plotly_chart(fig_sex)

# Гистограмма выживаемости по классу билета
fig_pclass = px.histogram(
    filtered_df,
    x="Pclass",
    color="Survived",
    barmode="group",
    title="Выживаемость по классу билета",
    labels={"Pclass": "Класс билета", "count": "Количество"},
    color_discrete_map={0: "red", 1: "green"}
)
st.plotly_chart(fig_pclass)

# Гистограмма выживаемости по возрасту
fig_age = px.histogram(
    filtered_df,
    x="Age",
    color="Survived",
    nbins=20,
    title="Выживаемость по возрасту",
    labels={"Age": "Возраст", "count": "Количество"},
    color_discrete_map={0: "red", 1: "green"}
)
st.plotly_chart(fig_age)

# Закрытие соединения с базой данных
conn.close()


