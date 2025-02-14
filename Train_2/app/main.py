from flask import Flask, render_template, request
import pickle

app = Flask(__name__)

@app.route("/")
def get_main_page():
    return render_template("index.html")

@app.route("/predict/", methods=['post', 'get'])
def get_prediction():
    if request.method == 'POST':
        columns = ["expenses_sum", "expenses_mean", "expenses_max", "expenses_min", "expenses_std", "region_turkey",
                   "channel_adnonsense", "device_iphone", "region_thailand", "channel_leapbob"]

        cluster_description = {
            0: "Cредний по кол-ву клиентов сегмент, данный сегмент пользователей требует средние затраты на рекламу (по сравнению с другими сегментами), минимальные затраты на рекламу при этом выше чем у других сегментов, с этого сегмента небольшая прибыль, в остальном - особо не выделяется.",
            1: "Данный сегмент пользователей самый немногочисленный, требует больше всего затрат на рекламу, скорее всего иностранцы (из Турции/Тайланда), скорее всего приходит за счёт иностранной рекламы (AdNonSense, LeapBob и других), приносит больше всего прибыли и посещает сайт больше всего за месяц.",
            2: "Данный сегмент пользователей самый многочисленный, он почти не требует затраты на рекламу (происходит через самостоятельный поиск сайта), в остальном - ничем не отличается от сегмента 0"
        }

        data = []
        for col in columns:
            value = float(request.form.get(col))
            data.append(value)

        filepath = "clustering_model.sav"

        model = pickle.load(open(filepath, "rb"))

        predicted_cluster = model.predict([data])[0]

        prediction = {
            "predicted_cluster": predicted_cluster,
            "description": cluster_description[predicted_cluster]
        }

        return render_template("index.html", prediction=prediction)


if __name__ == '__main__':
   app.run() 