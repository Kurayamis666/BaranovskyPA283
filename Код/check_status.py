# check_status.py
from database import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT request_id, request_status FROM requests")
requests = cursor.fetchall()
conn.close()

print("Текущие статусы заявок:")
for req in requests:
    print(f"  Заявка №{req['request_id']}: {req['request_status']}")