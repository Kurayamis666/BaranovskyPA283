# tests/test_import_data.py
"""Тесты модуля импорта данных."""
import unittest
import tempfile
from pathlib import Path
from utils.import_data import import_users, import_requests


class TestImportData(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_import_users_success(self):
        """Тест успешного импорта пользователей."""
        test_csv = self.test_dir / 'test_users.csv'
        test_csv.write_text(
            "userID;fio;phone;login;password;type\n"
            "99;Тестов Пользователь;89991234567;test_login;test_pass;Оператор\n",
            encoding='utf-8'
        )
        result = import_users(test_csv)
        self.assertEqual(result['success'], 1)
        self.assertEqual(result['errors'], 0)
    
    def test_import_users_file_not_found(self):
        """Тест обработки несуществующего файла."""
        result = import_users(self.test_dir / 'nonexistent.csv')
        self.assertEqual(result['errors'], 1)
        self.assertIn('не найден', result.get('message', '').lower())


if __name__ == '__main__':
    unittest.main(verbosity=2)