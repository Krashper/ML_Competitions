from flask import Flask, jsonify, request
from utils.model_prediction import predict  # Импорт ML модели

app = Flask(__name__)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.json
        result = round(predict(data['features'])[0])
        return jsonify({'prediction': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=5000)