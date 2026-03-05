# utils/statistics.py
"""Модуль расчёта статистики работы автосервиса."""
from database import get_connection


def get_total_requests():
    """Получить общее количество заявок."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM requests")
    result = cursor.fetchone()[0]
    connection.close()
    return result or 0


def get_completed_requests():
    """Получить количество завершённых заявок."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM requests WHERE request_status = 'Завершена'"
    )
    result = cursor.fetchone()[0]
    connection.close()
    return result or 0


def get_in_progress_requests():
    """Получить количество заявок в работе."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM requests WHERE request_status = 'В процессе ремонта'"
    )
    result = cursor.fetchone()[0]
    connection.close()
    return result or 0


def get_new_requests():
    """Получить количество новых заявок."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM requests WHERE request_status = 'Новая заявка'"
    )
    result = cursor.fetchone()[0]
    connection.close()
    return result or 0


def get_average_repair_time():
    """
    Рассчитать среднее время выполнения заявки в днях.
    
    Returns:
        float: Среднее время в днях (округлено до 1 знака)
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    # SQLite: julianday() для расчёта разницы дат
    cursor.execute('''
        SELECT ROUND(AVG(julianday(completion_date) - julianday(start_date)), 1)
        FROM requests
        WHERE completion_date IS NOT NULL 
          AND completion_date != 'null'
          AND request_status IN ('Завершена', 'Готова к выдаче')
    ''')
    
    result = cursor.fetchone()[0]
    connection.close()
    
    return round(result or 0, 1)


def get_top_issues(limit=5):
    """
    Получить список самых частых неисправностей.
    
    Args:
        limit: Количество записей для возврата
    
    Returns:
        list: Список кортежей (описание, количество)
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT problem_description, COUNT(*) as cnt
        FROM requests
        WHERE problem_description IS NOT NULL
        GROUP BY problem_description
        ORDER BY cnt DESC
        LIMIT ?
    ''', (limit,))
    
    result = cursor.fetchall()
    connection.close()
    
    return [(row[0], row[1]) for row in result]


def get_master_statistics():
    """
    Получить статистику по автомеханикам.
    
    Returns:
        list: Список словарей со статистикой по каждому механику
    """
    connection = get_connection()
    cursor = connection.cursor()
    
    cursor.execute('''
        SELECT 
            u.user_id,
            u.fio,
            COUNT(r.request_id) as total_requests,
            COUNT(CASE WHEN r.request_status = 'Завершена' THEN 1 END) as completed,
            ROUND(AVG(julianday(r.completion_date) - julianday(r.start_date)), 1) as avg_time
        FROM users u
        LEFT JOIN requests r ON u.user_id = r.master_id
        WHERE u.type = 'Автомеханик'
        GROUP BY u.user_id, u.fio
        HAVING COUNT(r.request_id) > 0
        ORDER BY completed DESC
    ''')
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'user_id': row[0],
            'fio': row[1],
            'total_requests': row[2] or 0,
            'completed': row[3] or 0,
            'avg_time': row[4] or 0
        })
    
    connection.close()
    return results


def get_full_statistics():
    """
    Получить полную статистику работы автосервиса.
    
    Returns:
        dict: Словарь со всеми метриками
    """
    return {
        'total_requests': get_total_requests(),
        'completed_requests': get_completed_requests(),
        'in_progress': get_in_progress_requests(),
        'new_requests': get_new_requests(),
        'average_repair_time': get_average_repair_time(),
        'top_issues': get_top_issues(),
        'master_statistics': get_master_statistics()
    }