from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.utils import PredictedModel
import pandas as pd
import uvicorn

# Инициализация приложения
app = FastAPI(title="Patient Survival API with HTML")

# Подключение шаблонов
templates = Jinja2Templates(directory="templates")

general_params = ["Age"]

ts_params = ['GCS', 'Urine', 'BUN', 'HR', 'WBC', 'Platelets',
    'HCO3', 'PAO2', 'Glucose', 'PaCO2', 'PH', 'Temp', 'Mg',
    'NIDiasABP', 'Na', 'HCT', 'NISysABP', 'K']

# Эндпоинт для отображения формы загрузки файла
@app.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    """
    Отображение HTML-формы для загрузки файла.
    """
    return templates.TemplateResponse("index.html", {"request": request})

# Эндпоинт для обработки файла
@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, file: UploadFile = File(...)):
    """
    Обработка файла и отображение результатов в HTML.
    """
    model = PredictedModel(general_params, ts_params, file.file, "app/mean_vals.csv", "app/reg_model.sav", "app/clf_model.sav")

    predictions = model.get_predictions()

    # Возврат результата в шаблон
    return templates.TemplateResponse("index.html", {
        "request": request,
        "life_expectancy_days": predictions["survival_days"],
        "survival_status": predictions["in_hosp_death"],
        "severity_indicator": predictions["indicator"]
    })

# Запуск приложения
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
