import pickle
import pandas as pd


def predict(features):
    try:
        features = pd.DataFrame(features)
        cat_cols = ["Gender"] # Категориальные признаки

        encoder = pickle.load(open("models/Encoder.sav", "rb"))

        encoded_features = encoder.transform(features[cat_cols])

        # Получаем имена новых колонок
        feature_names = encoder.get_feature_names_out(cat_cols)

        # Создаем DataFrame с закодированными данными
        features_encoded = pd.DataFrame(encoded_features, columns=feature_names)

        # Объединяем с числовыми колонками
        features = pd.concat([features.drop(cat_cols, axis=1), features_encoded], axis=1)

        scaler = pickle.load(open("models/Scaler.sav", "rb"))
        scaled_features = scaler.transform(features)

        model = pickle.load(open("models/Regression_Model.sav", "rb"))

        prediction = model.predict(scaled_features)

        return prediction

    except Exception as e:
        print("Ошибка:", e)