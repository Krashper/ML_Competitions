import dash
from dash import dcc, html, Input, Output
import pandas as pd
import sqlite3
import plotly.express as px

# Подключение к базе данных
conn = sqlite3.connect('titanic.db')

# Загрузка данных из базы данных
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

# Инициализация Dash-приложения
app = dash.Dash(__name__)
app.title = "Анализ выживаемости пассажиров Титаника 🚢"

# Макет приложения
app.layout = html.Div([
    html.H1("Анализ выживаемости пассажиров Титаника 🚢"),
    
    # Фильтры
    html.Div([
        html.Label("Выберите пол:"),
        dcc.Dropdown(
            id='sex-filter',
            options=[
                {'label': 'Все', 'value': 'Все'},
                {'label': 'Мужской', 'value': 'male'},
                {'label': 'Женский', 'value': 'female'}
            ],
            value='Все'
        ),
        
        html.Label("Выберите класс билета:"),
        dcc.Dropdown(
            id='pclass-filter',
            options=[
                {'label': 'Все', 'value': 'Все'},
                {'label': '1 класс', 'value': 1},
                {'label': '2 класс', 'value': 2},
                {'label': '3 класс', 'value': 3}
            ],
            value='Все'
        ),
        
        html.Label("Выберите возрастной диапазон:"),
        dcc.RangeSlider(
            id='age-filter',
            min=0,
            max=100,
            step=1,
            marks={i: str(i) for i in range(0, 101, 10)},
            value=[0, 100]
        )
    ], style={'margin-bottom': '20px'}),
    
    # Графики
    dcc.Graph(id='survival-pie-chart'),
    dcc.Graph(id='survival-by-sex'),
    dcc.Graph(id='survival-by-pclass'),
    dcc.Graph(id='survival-by-age')
])

# Callback для обновления графиков
@app.callback(
    [Output('survival-pie-chart', 'figure'),
     Output('survival-by-sex', 'figure'),
     Output('survival-by-pclass', 'figure'),
     Output('survival-by-age', 'figure')],
    [Input('sex-filter', 'value'),
     Input('pclass-filter', 'value'),
     Input('age-filter', 'value')]
)
def update_graphs(sex_filter, pclass_filter, age_filter):
    # Применение фильтров
    filtered_df = df.copy()
    if sex_filter != 'Все':
        filtered_df = filtered_df[filtered_df['Sex'] == sex_filter]
    if pclass_filter != 'Все':
        filtered_df = filtered_df[filtered_df['Pclass'] == pclass_filter]
    filtered_df = filtered_df[(filtered_df['Age'] >= age_filter[0]) & (filtered_df['Age'] <= age_filter[1])]
    
    # Круговая диаграмма выживаемости
    survived_counts = filtered_df['Survived'].value_counts().rename({0: "Погиб", 1: "Выжил"})
    pie_chart = px.pie(
        survived_counts,
        values=survived_counts.values,
        names=survived_counts.index,
        title="Соотношение выживших и погибших"
    )
    
    # Гистограмма выживаемости по полу
    sex_chart = px.histogram(
        filtered_df,
        x='Sex',
        color='Survived',
        barmode='group',
        title="Выживаемость по полу",
        labels={'Sex': 'Пол', 'count': 'Количество'},
        color_discrete_map={0: "red", 1: "green"}
    )
    
    # Гистограмма выживаемости по классу билета
    pclass_chart = px.histogram(
        filtered_df,
        x='Pclass',
        color='Survived',
        barmode='group',
        title="Выживаемость по классу билета",
        labels={'Pclass': 'Класс билета', 'count': 'Количество'},
        color_discrete_map={0: "red", 1: "green"}
    )
    
    # Гистограмма выживаемости по возрасту
    age_chart = px.histogram(
        filtered_df,
        x='Age',
        color='Survived',
        nbins=20,
        title="Выживаемость по возрасту",
        labels={'Age': 'Возраст', 'count': 'Количество'},
        color_discrete_map={0: "red", 1: "green"}
    )

    return pie_chart, sex_chart, pclass_chart, age_chart


if __name__ == '__main__':
    app.run_server(debug=True)