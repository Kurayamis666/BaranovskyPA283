# utils/import_data.py
"""Модуль импорта данных из CSV-файлов в базу данных."""
import csv
from pathlib import Path
from database import get_connection


DATA_DIR = Path(__file__).parent.parent / 'data' / 'imports'


def import_users(csv_path=None):
    """
    Импортировать пользователей из CSV-файла в таблицу users.
    
    Args:
        csv_path: Путь к CSV-файлу (по умолчанию: data/imports/inputDataUsers.csv)
    
    Returns:
        dict: Статистика импорта (успешно, ошибок)
    """
    if csv_path is None:
        csv_path = DATA_DIR / 'inputDataUsers.csv'
    
    if not csv_path.exists():
        return {'success': 0, 'errors': 1, 'message': f'Файл не найден: {csv_path}'}
    
    connection = get_connection()
    cursor = connection.cursor()
    
    success_count = 0
    error_count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            for row in reader:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO users 
                        (user_id, fio, phone, login, password, type)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        int(row['userID']),
                        row['fio'],
                        row['phone'],
                        row['login'],
                        row['password'],
                        row['type']
                    ))
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Ошибка импорта пользователя {row.get('userID')}: {e}")
        
        connection.commit()
        return {'success': success_count, 'errors': error_count}
    
    except Exception as e:
        return {'success': 0, 'errors': 1, 'message': str(e)}
    
    finally:
        connection.close()


def import_requests(csv_path=None):
    """
    Импортировать заявки из CSV-файла в таблицу requests.
    
    Args:
        csv_path: Путь к CSV-файлу
    
    Returns:
        dict: Статистика импорта
    """
    if csv_path is None:
        csv_path = DATA_DIR / 'inputDataRequests.csv'
    
    if not csv_path.exists():
        return {'success': 0, 'errors': 1, 'message': f'Файл не найден: {csv_path}'}
    
    connection = get_connection()
    cursor = connection.cursor()
    
    success_count = 0
    error_count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            for row in reader:
                try:
                    # Обработка null значений
                    master_id = int(row['masterID']) if row['masterID'] and row['masterID'] != 'null' else None
                    client_id = int(row['clientID']) if row['clientID'] and row['clientID'] != 'null' else None
                    completion_date = row['completionDate'] if row['completionDate'] and row['completionDate'] != 'null' else None
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO requests 
                        (request_id, start_date, car_type, car_model, problem_description,
                         request_status, completion_date, repair_parts, master_id, client_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        int(row['requestID']),
                        row['startDate'],
                        row['carType'],
                        row['carModel'],
                        row['problemDescryption'],
                        row['requestStatus'],
                        completion_date,
                        row.get('repairParts', ''),
                        master_id,
                        client_id
                    ))
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Ошибка импорта заявки {row.get('requestID')}: {e}")
        
        connection.commit()
        return {'success': success_count, 'errors': error_count}
    
    except Exception as e:
        return {'success': 0, 'errors': 1, 'message': str(e)}
    
    finally:
        connection.close()


def import_comments(csv_path=None):
    """
    Импортировать комментарии из CSV-файла в таблицу comments.
    
    Args:
        csv_path: Путь к CSV-файлу
    
    Returns:
        dict: Статистика импорта
    """
    if csv_path is None:
        csv_path = DATA_DIR / 'inputDataComments.csv'
    
    if not csv_path.exists():
        return {'success': 0, 'errors': 1, 'message': f'Файл не найден: {csv_path}'}
    
    connection = get_connection()
    cursor = connection.cursor()
    
    success_count = 0
    error_count = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            for row in reader:
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO comments 
                        (comment_id, message, master_id, request_id)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        int(row['commentID']),
                        row['message'],
                        int(row['masterID']),
                        int(row['requestID'])
                    ))
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Ошибка импорта комментария {row.get('commentID')}: {e}")
        
        connection.commit()
        return {'success': success_count, 'errors': error_count}
    
    except Exception as e:
        return {'success': 0, 'errors': 1, 'message': str(e)}
    
    finally:
        connection.close()


def import_all_data():
    """
    Импортировать все данные из CSV-файлов.
    
    Returns:
        dict: Общая статистика импорта
    """
    results = {
        'users': import_users(),
        'requests': import_requests(),
        'comments': import_comments()
    }
    
    total_success = sum(r.get('success', 0) for r in results.values())
    total_errors = sum(r.get('errors', 0) for r in results.values())
    
    return {
        'details': results,
        'total_success': total_success,
        'total_errors': total_errors
    }