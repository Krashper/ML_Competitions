from flask import Flask, render_template, request
import requests

app = Flask(__name__)
API_URL = 'http://127.0.0.1:5000/api/predict'

@app.route('/')
def index():
    return render_template('index.html')

# Создано в целях примера обработки данных
@app.route('/fake_predict', methods=['POST'])
def fake_predict():
    try:
        features = {
            "Name": request.form["customer_name"],
            "Gender": request.form["Gender"],
            "Age": int(request.form["Age"]),
            "Comments": request.form["comments"],
            "Customer_Type": request.form["customer_type"],
            "Preferences": request.form.getlist("preferences")
        }

        print(features)

        # Обработка файла
        file = request.files["customer_photo"]

        file.save(f"static/uploads/{file.filename}")

        return render_template("index.html")

    except Exception as e:
        print("Ошибка:", e)
        return render_template("index.html")

# Эндпоинт для предсказания
@app.route('/predict', methods=['POST'])
def web_predict():
    try:
        features = {
            "Gender": [request.form["Gender"]],
            "Age": [float(request.form['Age'])],
            "Annual Income (k$)": [float(request.form['Annual Income (k$)'])]
        }
        response = requests.post(API_URL, json={'features': features})
        return render_template('index.html', 
                            prediction=response.json()['prediction'])
    except Exception as e:
        return render_template('index.html', 
                            error=str(e))


if __name__ == '__main__':
    app.run(port=8000)