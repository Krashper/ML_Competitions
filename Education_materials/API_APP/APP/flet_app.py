import flet as ft
import pandas as pd
from model import predict_value

def main(page: ft.Page):
    page.title = "Medical Data Input"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Поля ввода
    entry_sgot_ast = ft.TextField(label="SGOT_AST")
    entry_sgot_alt = ft.TextField(label="SGOT_ALT")
    entry_triglyceride = ft.TextField(label="Triglyceride")
    sex_var = ft.RadioGroup(content=ft.Column([
        ft.Radio(value="Male", label="Male"),
        ft.Radio(value="Female", label="Female")
    ]))
    entry_hemoglobin = ft.TextField(label="Hemoglobin")
    entry_weight = ft.TextField(label="Weight")
    entry_waistline = ft.TextField(label="Waistline")
    entry_blds = ft.TextField(label="BLDS")
    entry_dbp = ft.TextField(label="DBP")
    entry_height = ft.TextField(label="Height")
    entry_sbp = ft.TextField(label="SBP")
    result_field = ft.Text("Результат:")

    # Функция для обработки отправки данных
    def submit(e):
        data = {
            "SGOT_AST": [float(entry_sgot_ast.value)],
            "SGOT_ALT": [float(entry_sgot_alt.value)],
            "triglyceride": [float(entry_triglyceride.value)],
            "sex": [sex_var.value],
            "hemoglobin": [float(entry_hemoglobin.value)],
            "weight": [float(entry_weight.value)],
            "waistline": [float(entry_waistline.value)],
            "BLDS": [float(entry_blds.value)],
            "DBP": [float(entry_dbp.value)],
            "height": [float(entry_height.value)],
            "SBP": [float(entry_sbp.value)]
        }

        # Создаем DataFrame из словаря
        df = pd.DataFrame(data)

        # Получаем предсказание
        response_data = predict_value(df.to_json())

        print(response_data)
        # Показываем результат
        # page.dialog = ft.AlertDialog(
        #     title=ft.Text("Prediction Result"),
        #     content=ft.Text(str(response_data)),
        #     on_dismiss=lambda e: print("Dialog dismissed!")
        # )
        # page.dialog.open = True
        result_field.value = "Результат:"+str(response_data)
        page.update()

    # Кнопка отправки данных
    submit_button = ft.ElevatedButton("Submit", on_click=submit)

    # Добавляем все элементы на страницу
    page.add(
        entry_sgot_ast,
        entry_sgot_alt,
        entry_triglyceride,
        ft.Text("Sex:"),
        sex_var,
        entry_hemoglobin,
        entry_weight,
        entry_waistline,
        entry_blds,
        entry_dbp,
        entry_height,
        entry_sbp,
        result_field,
        submit_button
        
    )

# Запуск приложения
ft.app(target=main, view=ft.WEB_BROWSER)