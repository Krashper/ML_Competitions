from flask import Flask, render_template, request, redirect, url_for
import os
import numpy as np
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route("/")
def get_main_page():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def get_prediction():
    prediction = None

    try:
        if request.method == 'POST':
            text_data = request.form.get('text_data', '')
            numeric_data = request.form.get('numeric_data', '')
            categorical_data = request.form.get('categorical_data', '')

            try:
                numeric_value = float(numeric_data)
                categorical_value = 1 if categorical_data == 'category1' else 2 if categorical_data == 'category2' else 3
            except ValueError as ve:
                raise ValueError("Ошибка: не переданы все числовые признаки")

            # Заглушка вместо модели
            prediction = f"Заглушка: num={numeric_value}, cat={categorical_value}"

            file = request.files.get('file')
            if file and allowed_file(file.filename):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    except Exception as e:
        prediction = f"{str(e)}"

    return render_template('index.html', prediction=prediction)


if __name__ == '__main__':
    app.run(debug=True)
