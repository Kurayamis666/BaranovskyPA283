# check_db.py
from database import get_connection
from pathlib import Path

# Показываем путь к БД
db_path = Path(__file__).parent / 'data' / 'auto_service.db'
print(f"=== ПУТЬ К БАЗЕ ДАННЫХ ===")
print(f"Path: {db_path.absolute()}")
print(f"Exists: {db_path.exists()}\n")

conn = get_connection()
cursor = conn.cursor()

print("=== ТЕКУЩИЕ СТАТУСЫ ЗАЯВОК ===")
cursor.execute("SELECT request_id, request_status FROM requests")
for row in cursor.fetchall():
    print(f"  Заявка {row[0]}: '{row[1]}'")

conn.close()