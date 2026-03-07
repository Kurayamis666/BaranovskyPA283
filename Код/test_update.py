# test_update.py
"""Прямой тест обновления статуса в БД."""
from database import get_connection

def test_update():
    """Прямое обновление статуса заявки №1."""
    print("🔧 Тест прямого обновления БД...")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Проверяем текущий статус
    cursor.execute("SELECT request_status FROM requests WHERE request_id = 1")
    before = cursor.fetchone()
    print(f"Статус ДО: '{before[0] if before else 'NULL'}'")
    
    # Обновляем
    cursor.execute('''
        UPDATE requests 
        SET request_status = 'Завершена'
        WHERE request_id = 1
    ''')
    
    print(f"Обновлено строк: {cursor.rowcount}")
    
    conn.commit()
    
    # Проверяем после
    cursor.execute("SELECT request_status FROM requests WHERE request_id = 1")
    after = cursor.fetchone()
    print(f"Статус ПОСЛЕ: '{after[0] if after else 'NULL'}'")
    
    conn.close()
    
    if after and after[0] == 'Завершена':
        print("✅ Тест ПРОЙДЕН: статус обновился!")
    else:
        print("❌ Тест НЕ ПРОЙДЕН: статус НЕ обновился!")

if __name__ == '__main__':
    test_update()