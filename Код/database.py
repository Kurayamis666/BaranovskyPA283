# database.py
"""Модуль работы с базой данных SQLite."""
import sqlite3
from pathlib import Path

# Путь к базе данных
DATABASE_PATH = Path(__file__).parent / 'data' / 'auto_service.db'

def get_connection():
    """Получить соединение с базой данных."""
    # ✅ Автоматически создаём папку, если нет
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_database():
    """Создать таблицы базы данных если они не существуют."""
    connection = get_connection()
    cursor = connection.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            fio TEXT NOT NULL,
            phone TEXT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN (
                'Менеджер', 'Автомеханик', 'Оператор', 'Заказчик', 'Менеджер по качеству'
            ))
        )
    ''')
    
    # Таблица заявок
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            request_id INTEGER PRIMARY KEY,
            start_date TEXT NOT NULL,
            car_type TEXT,
            car_model TEXT,
            problem_description TEXT,
            request_status TEXT NOT NULL CHECK(request_status IN (
                'Новая заявка', 'В процессе ремонта', 'Готова к выдаче', 'Завершена', 'Ожидание запчастей'
            )),
            completion_date TEXT,
            repair_parts TEXT,
            master_id INTEGER,
            client_id INTEGER,
            FOREIGN KEY (master_id) REFERENCES users(user_id) ON DELETE SET NULL,
            FOREIGN KEY (client_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')
    
    # Таблица комментариев
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            comment_id INTEGER PRIMARY KEY,
            message TEXT NOT NULL,
            master_id INTEGER,
            request_id INTEGER NOT NULL,
            FOREIGN KEY (master_id) REFERENCES users(user_id) ON DELETE SET NULL,
            FOREIGN KEY (request_id) REFERENCES requests(request_id) ON DELETE CASCADE
        )
    ''')
    
    # Таблица опросов качества
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quality_surveys (
            survey_id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER UNIQUE NOT NULL,
            qr_code TEXT,
            survey_link TEXT,
            rating INTEGER CHECK(rating BETWEEN 1 AND 5),
            feedback TEXT,
            FOREIGN KEY (request_id) REFERENCES requests(request_id) ON DELETE CASCADE
        )
    ''')
    
    connection.commit()
    connection.close()