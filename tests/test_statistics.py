# tests/test_statistics.py
"""Тесты модуля статистики."""
import unittest
from utils.statistics import get_total_requests, get_average_repair_time, get_top_issues


class TestStatistics(unittest.TestCase):
    
    def test_get_total_requests_returns_int(self):
        """Тест: общее количество заявок — целое число."""
        result = get_total_requests()
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
    
    def test_average_repair_time_is_float(self):
        """Тест: среднее время — float >= 0."""
        result = get_average_repair_time()
        self.assertIsInstance(result, (int, float))
        self.assertGreaterEqual(result, 0)
    
    def test_top_issues_returns_list(self):
        """Тест: топ неисправностей — список кортежей."""
        result = get_top_issues(limit=3)
        self.assertIsInstance(result, list)
        if result:
            self.assertIsInstance(result[0], tuple)
            self.assertEqual(len(result[0]), 2)


if __name__ == '__main__':
    unittest.main(verbosity=2)