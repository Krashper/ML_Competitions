import requests
import pandas as pd


def predict_value(data_json):
    response = requests.post('http://127.0.0.1:5000/get_gammagpt',json=data_json)
    df_return = pd.read_json(response.json())
    return df_return['prediction'].values[0]