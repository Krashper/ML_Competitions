import tkinter as tk
from tkinter import messagebox
import pandas as pd
from model import predict_value

def submit():
    # Получаем данные из полей ввода
    data = {
        "SGOT_AST": [float(entry_sgot_ast.get())],
        "SGOT_ALT": [float(entry_sgot_alt.get())],
        "triglyceride": [float(entry_triglyceride.get())],
        "sex": [sex_var.get()],
        "hemoglobin": [float(entry_hemoglobin.get())],
        "weight": [float(entry_weight.get())],
        "waistline": [float(entry_waistline.get())],
        "BLDS": [float(entry_blds.get())],
        "DBP": [float(entry_dbp.get())],
        "height": [float(entry_height.get())],
        "SBP": [float(entry_sbp.get())]
    }
    
    # Создаем DataFrame из словаря
    df = pd.DataFrame(data)

    response_data = predict_value(df.to_json())
    messagebox.showinfo("Info", str(response_data))


# Создаем главное окно
root = tk.Tk()
root.title("Medical Data Input")

# Создаем и размещаем элементы интерфейса
tk.Label(root, text="SGOT_AST:").grid(row=0, column=0)
entry_sgot_ast = tk.Entry(root)
entry_sgot_ast.grid(row=0, column=1)

tk.Label(root, text="SGOT_ALT:").grid(row=1, column=0)
entry_sgot_alt = tk.Entry(root)
entry_sgot_alt.grid(row=1, column=1)

tk.Label(root, text="Triglyceride:").grid(row=2, column=0)
entry_triglyceride = tk.Entry(root)
entry_triglyceride.grid(row=2, column=1)

tk.Label(root, text="Sex:").grid(row=3, column=0)
sex_var = tk.StringVar(value="Male")
tk.Radiobutton(root, text="Male", variable=sex_var, value="Male").grid(row=3, column=1)
tk.Radiobutton(root, text="Female", variable=sex_var, value="Female").grid(row=3, column=2)

tk.Label(root, text="Hemoglobin:").grid(row=4, column=0)
entry_hemoglobin = tk.Entry(root)
entry_hemoglobin.grid(row=4, column=1)

tk.Label(root, text="Weight:").grid(row=5, column=0)
entry_weight = tk.Entry(root)
entry_weight.grid(row=5, column=1)

tk.Label(root, text="Waistline:").grid(row=6, column=0)
entry_waistline = tk.Entry(root)
entry_waistline.grid(row=6, column=1)

tk.Label(root, text="BLDS:").grid(row=7, column=0)
entry_blds = tk.Entry(root)
entry_blds.grid(row=7, column=1)

tk.Label(root, text="DBP:").grid(row=8, column=0)
entry_dbp = tk.Entry(root)
entry_dbp.grid(row=8, column=1)

tk.Label(root, text="Height:").grid(row=9, column=0)
entry_height = tk.Entry(root)
entry_height.grid(row=9, column=1)

tk.Label(root, text="SBP:").grid(row=10, column=0)
entry_sbp = tk.Entry(root)
entry_sbp.grid(row=10, column=1)

# Кнопка отправки данных
tk.Button(root, text="Submit", command=submit).grid(row=11, column=0, columnspan=2)

# Запуск главного цикла
root.mainloop()