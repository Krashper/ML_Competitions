from flask import Flask, render_template, request
import requests
from sqlalchemy import create_engine
from dotenv import dotenv_values
import pandas as pd

app = Flask(__name__)
API_URL = 'http://127.0.0.1:5000/api/predict'

def get_conn(dbname, user, password, host):
    url = f"postgresql+psycopg2://{user}:{password}@{host}/{dbname}"
    return create_engine(url)

config = dotenv_values(".env")
dbname = config.get('dbname') # Название базы данных
user = config.get('user') # Имя пользователя для подключения
password = config.get('password') # Пароль пользователя для подключения
host = config.get('host') # Хост

conn = get_conn(dbname, user, password, host)

data = pd.read_sql("SELECT * FROM water_pollution", conn)

countries = data["Country"].unique()
regions = data["Region"].unique()
water_types = data["Water Source Type"].unique()
treatment_methods = data["Water Treatment Method"].unique()

@app.route('/')
def index():
    return render_template('index.html', 
                           countries=countries, regions=regions,
                           water_types=water_types, treatment_methods=treatment_methods)


# Эндпоинт для предсказания
@app.route('/predict', methods=['POST'])
def web_predict():
    try:
        features = {
            "Country": [request.form["Country"]],
            "Region": [request.form['Region']],
            "Year": [float(request.form['Year'])],
            "Water Source Type": [request.form['Water Source Type']],
            "Contaminant Level (ppm)": [float(request.form['Contaminant Level (ppm)'])],
            "pH Level": [float(request.form['pH Level'])],
            "Turbidity (NTU)": [float(request.form['Turbidity (NTU)'])],
            "Dissolved Oxygen (mg/L)": [float(request.form['Dissolved Oxygen (mg/L)'])],
            "Nitrate Level (mg/L)": [float(request.form['Nitrate Level (mg/L)'])],
            "Lead Concentration (µg/L)": [float(request.form['Lead Concentration (µg/L)'])],
            "Bacteria Count (CFU/mL)": [float(request.form['Bacteria Count (CFU/mL)'])],
            "Water Treatment Method": [request.form['Water Treatment Method']],
            "Access to Clean Water (% of Population)": [float(request.form['Access to Clean Water (% of Population)'])],
            "Diarrheal Cases per 100,000 people": [float(request.form['Diarrheal Cases per 100,000 people'])],
            "Cholera Cases per 100,000 people": [float(request.form['Cholera Cases per 100,000 people'])],
            "Typhoid Cases per 100,000 people": [float(request.form['Typhoid Cases per 100,000 people'])],
            "Infant Mortality Rate (per 1,000 live births)": [float(request.form['Infant Mortality Rate (per 1,000 live births)'])],
            "GDP per Capita (USD)": [float(request.form['GDP per Capita (USD)'])],
            "Healthcare Access Index (0-100)": [float(request.form['Healthcare Access Index (0-100)'])],
            "Urbanization Rate (%)": [float(request.form['Urbanization Rate (%)'])],
            "Sanitation Coverage (% of Population)": [float(request.form['Sanitation Coverage (% of Population)'])],
            "Rainfall (mm per year)": [float(request.form['Rainfall (mm per year)'])],
            "Temperature (°C)": [float(request.form['Temperature (°C)'])]
        }
        response = requests.post(API_URL, json={'features': features})
        return render_template('index.html', 
                            prediction=response.json()['prediction'],
                            countries=countries, regions=regions,
                            water_types=water_types, treatment_methods=treatment_methods)
    except Exception as e:
        return render_template('index.html', 
                            error=str(e),
                            countries=countries, regions=regions,
                            water_types=water_types, treatment_methods=treatment_methods)


if __name__ == '__main__':
    app.run(port=8000)