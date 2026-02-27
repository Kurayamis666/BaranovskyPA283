# tests/test_business_logic.py
"""Тесты бизнес-логики модуля."""
import unittest
from utils.statistics import get_full_statistics, get_average_repair_time
from utils.import_data import import_all_data


class TestBusinessLogic(unittest.TestCase):
    """Тесты бизнес-логики."""
    
    def test_import_data(self):
        """Тест импорта данных из CSV."""
        result = import_all_data()
        self.assertGreater(result['total_success'], 0)
    
    def test_statistics(self):
        """Тест расчёта статистики."""
        stats = get_full_statistics()
        self.assertIn('total_requests', stats)
        self.assertIn('average_repair_time', stats)
        self.assertIsInstance(stats['total_requests'], int)
    
    def test_average_repair_time(self):
        """Тест среднего времени ремонта."""
        avg_time = get_average_repair_time()
        self.assertIsInstance(avg_time, float)
        self.assertGreaterEqual(avg_time, 0)


if __name__ == '__main__':
    unittest.main()