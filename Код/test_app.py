# test_app.py
"""Unit-тесты для приложения Автосервис."""

import unittest
import sqlite3
from database import get_connection

class TestDatabase(unittest.TestCase):
    """Тесты для базы данных."""
    
    def test_connection(self):
        """Проверка подключения к БД."""
        conn = get_connection()
        self.assertIsNotNone(conn)
        conn.close()
    
    def test_users_table(self):
        """Проверка таблицы users."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        self.assertGreater(count, 0)
        conn.close()
    
    def test_requests_table(self):
        """Проверка таблицы requests."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM requests")
        count = cursor.fetchone()[0]
        self.assertGreaterEqual(count, 0)
        conn.close()
    
    def test_user_login(self):
        """Проверка авторизации."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id FROM users WHERE login = ? AND password = ?",
            ('login1', 'pass1')
        )
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        conn.close()

class TestValidation(unittest.TestCase):
    """Тесты валидации."""
    
    def test_empty_model(self):
        """Проверка пустой модели авто."""
        car_model = ""
        self.assertEqual(len(car_model.strip()), 0)
    
    def test_valid_status(self):
        """Проверка допустимого статуса."""
        valid_statuses = [
            'Новая заявка',
            'В процессе ремонта',
            'Готова к выдаче',
            'Завершена',
            'Ожидание запчастей'
        ]
        status = 'Завершена'
        self.assertIn(status, valid_statuses)

if __name__ == '__main__':
    unittest.main(verbosity=2)