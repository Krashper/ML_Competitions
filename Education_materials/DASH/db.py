import sqlite3
import pandas as pd

# Подключение к базе данных
conn = sqlite3.connect('titanic.db')
cursor = conn.cursor()

# Чтение CSV-файла
df = pd.read_csv('titanic.csv')

# Заполнение таблицы Passengers
for _, row in df.iterrows():
    cursor.execute('''
    INSERT INTO Passengers (PassengerId, Name, Sex, Age, Survived, Pclass)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (row['PassengerId'], row['Name'], row['Sex'], row['Age'], row['Survived'], row['Pclass']))

# Заполнение таблицы Tickets
for _, row in df.iterrows():
    cursor.execute('''
    INSERT INTO Tickets (TicketNumber, Fare, Cabin, Embarked)
    VALUES (?, ?, ?, ?)
    ''', (row['Ticket'], row['Fare'], row['Cabin'], row['Embarked']))

# Получение TicketId для связей
cursor.execute('SELECT TicketId, TicketNumber FROM Tickets')
ticket_mapping = {ticket_number: ticket_id for ticket_id, ticket_number in cursor.fetchall()}

# Заполнение таблицы PassengerTickets
for _, row in df.iterrows():
    ticket_id = ticket_mapping[row['Ticket']]
    cursor.execute('''
    INSERT INTO PassengerTickets (PassengerId, TicketId)
    VALUES (?, ?)
    ''', (row['PassengerId'], ticket_id))

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()