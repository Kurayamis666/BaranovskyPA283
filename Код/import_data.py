# import_data.py
"""Скрипт импорта данных из CSV в SQLite."""
import csv
import sqlite3
from pathlib import Path
from database import get_connection, initialize_database

def detect_encoding(filepath):
    """Определить кодировку файла."""
    encodings = ['utf-8', 'cp1251', 'utf-8-sig', 'latin-1']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                f.read()
            return encoding
        except UnicodeDecodeError:
            continue
    return 'utf-8'  # по умолчанию

def import_users():
    """Импорт пользователей."""
    conn = get_connection()
    cursor = conn.cursor()
    
    csv_path = Path(__file__).parent / 'inputDataUsers.csv'
    encoding = detect_encoding(csv_path)
    print(f"   Кодировка users: {encoding}")
    
    with open(csv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            cursor.execute('''
                INSERT OR REPLACE INTO users (user_id, fio, phone, login, password, type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                int(row['userID']), row['fio'], row['phone'],
                row['login'], row['password'], row['type']
            ))
    
    conn.commit()
    conn.close()
    print("✅ Пользователи импортированы")

def import_requests():
    """Импорт заявок."""
    conn = get_connection()
    cursor = conn.cursor()
    
    csv_path = Path(__file__).parent / 'inputDataRequests.csv'
    encoding = detect_encoding(csv_path)
    print(f"   Кодировка requests: {encoding}")
    
    with open(csv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            master_id = int(row['masterID']) if row['masterID'] and row['masterID'] != 'null' else None
            client_id = int(row['clientID']) if row['clientID'] and row['clientID'] != 'null' else None
            completion_date = row['completionDate'] if row['completionDate'] and row['completionDate'] != 'null' else None
            
            cursor.execute('''
                INSERT OR REPLACE INTO requests 
                (request_id, start_date, car_type, car_model, problem_description,
                 request_status, completion_date, repair_parts, master_id, client_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                int(row['requestID']), row['startDate'], row['carType'],
                row['carModel'], row['problemDescryption'], row['requestStatus'],
                completion_date, row.get('repairParts', ''), master_id, client_id
            ))
    
    conn.commit()
    conn.close()
    print("✅ Заявки импортированы")

def import_comments():
    """Импорт комментариев."""
    conn = get_connection()
    cursor = conn.cursor()
    
    csv_path = Path(__file__).parent / 'inputDataComments.csv'
    encoding = detect_encoding(csv_path)
    print(f"   Кодировка comments: {encoding}")
    
    with open(csv_path, 'r', encoding=encoding) as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            cursor.execute('''
                INSERT OR REPLACE INTO comments (comment_id, message, master_id, request_id)
                VALUES (?, ?, ?, ?)
            ''', (
                int(row['commentID']), row['message'],
                int(row['masterID']), int(row['requestID'])
            ))
    
    conn.commit()
    conn.close()
    print("✅ Комментарии импортированы")

if __name__ == '__main__':
    print("🚀 Инициализация базы данных...")
    initialize_database()
    
    print("\n📥 Импорт данных...")
    import_users()
    import_requests()
    import_comments()
    
    print("\n🎉 Готово! Можно запускать приложение:")
    print("   py -3.14 main.py")