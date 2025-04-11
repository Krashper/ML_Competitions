import pickle
import pandas as pd


def get_encoded_data(data):
    cat = ["object"]

    cat_data = data.select_dtypes(include=cat)

    cat_cols = cat_data.columns # Категориальные признаки

    encoder = pickle.load(open("models/Encoder.sav", "rb"))
    encoded_data = encoder.transform(data[cat_cols])

    # Получаем имена новых колонок
    feature_names = encoder.get_feature_names_out(cat_cols)

    # Создаем DataFrame с закодированными данными
    data_encoded = pd.DataFrame(encoded_data, columns=feature_names)

    # Объединяем с числовыми колонками
    data = pd.concat([data.drop(cat_cols, axis=1), data_encoded], axis=1)
    return data

def get_scaled_data(data):
    scaler = pickle.load(open("models/Scaler.sav", "rb"))
    scaled_data = scaler.transform(data)

    scaled_data = pd.DataFrame(scaled_data, columns=data.columns)

    return scaled_data

def get_pca_data(data):
    pca = pickle.load(open("models/PCA.sav", "rb"))
    pca_data = pca.transform(data)

    return pca_data

def predict(features):
    try:
        features = pd.DataFrame(features)
        features = get_encoded_data(features)

        scaled_features = get_scaled_data(features)

        pca_features = get_pca_data(scaled_features)

        model = pickle.load(open("models/GradientBoostingRegressor.sav", "rb"))

        prediction = model.predict(pca_features)

        return prediction

    except Exception as e:
        print("Ошибка:", e)