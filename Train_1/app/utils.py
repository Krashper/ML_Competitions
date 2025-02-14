import pandas as pd
from typing import List
import numpy as np
import pickle


class PredictedModel:
    def __init__(self, general_params, ts_params, file_path, mean_vals_path, reg_model_path, clf_model_path):
        self.general_params = general_params
        self.ts_params = ts_params
        self.file_path = file_path
        self.mean_vals_path = mean_vals_path
        self.reg_model_path = reg_model_path
        self.clf_model_path = clf_model_path

    def __get_patient_data(self):
        patient_params = []
        data = pd.read_csv(self.file_path)

        # Получение общих параметров
        for param in self.general_params:
            try:
                param_value = data[data["Parameter"] == param]["Value"].iloc[0]
                patient_params.append(param_value)
            except IndexError:
                patient_params.append(None)

        # Получение среднего значения временных параметров
        for param in self.ts_params:
            try:
                param_value = data[data["Parameter"] == param]["Value"].mean()
                patient_params.append(param_value)
            except IndexError:
                patient_params.append(None)

        return patient_params

    def __create_dataset(self):
        patient_params = self.__get_patient_data()

        mean_params = ["Mean" + ts_param for ts_param in self.ts_params]
        dataset = pd.DataFrame(columns=self.general_params + mean_params, data=[patient_params])

        mean_vals = pd.read_csv(self.mean_vals_path, index_col=0)["0"]

        mean_vals = mean_vals.reindex(dataset.columns)

        # Этап 4: Заполним NaN значения
        dataset = dataset.fillna(mean_vals)

        return dataset

    def __get_survival_prediction(self, X: pd.DataFrame):
        model = pickle.load(open(self.reg_model_path, 'rb'))

        prediction = model.predict(X)

        return prediction[0]

    def __get_hosp_death_prediction(self, X: pd.DataFrame):
        model = pickle.load(open(self.clf_model_path, 'rb'))

        prediction = model.predict(X)

        return prediction[0]

    def __get_indicator_color(self, survival_pred, in_hosp_death_pred):
        if survival_pred > 365:
            if in_hosp_death_pred == 0:
                return "green"
            else:
                return "yellow"

        else:
            if in_hosp_death_pred == 0:
                return "yellow"
            else:
                return "red"

    def get_predictions(self):
        dataset = self.__create_dataset()
        survival_prediction = self.__get_survival_prediction(dataset)
        in_hosp_death_prediction = self.__get_hosp_death_prediction(dataset)
        indicator = self.__get_indicator_color(survival_prediction, in_hosp_death_prediction)

        return {
            "survival_days": int(survival_prediction),
            "in_hosp_death": in_hosp_death_prediction,
            "indicator": indicator
        }
