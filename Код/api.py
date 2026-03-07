# api.py
from flask import Flask, jsonify, request
from database import get_connection

app = Flask(__name__)

@app.route('/api/requests', methods=['GET'])
def get_requests():
    """Получить все заявки."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.request_id, r.start_date, r.car_type, r.car_model,
               r.problem_description, r.request_status, r.completion_date,
               c.fio as client_name, m.fio as master_name
        FROM requests r
        LEFT JOIN users c ON r.client_id = c.user_id
        LEFT JOIN users m ON r.master_id = m.user_id
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'success': True,
        'count': len(rows),
        'requests': [
            {
                'request_id': row[0],
                'start_date': row[1],
                'car_type': row[2],
                'car_model': row[3],
                'problem_description': row[4],
                'request_status': row[5],
                'completion_date': row[6],
                'client_name': row[7],
                'master_name': row[8]
            } for row in rows
        ]
    })

@app.route('/api/requests/<int:request_id>', methods=['GET'])
def get_request(request_id):
    """Получить заявку по ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.request_id, r.start_date, r.car_type, r.car_model,
               r.problem_description, r.request_status,
               c.fio as client_name, m.fio as master_name
        FROM requests r
        LEFT JOIN users c ON r.client_id = c.user_id
        LEFT JOIN users m ON r.master_id = m.user_id
        WHERE r.request_id = ?
    ''', (request_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            'success': True,
            'request': {
                'request_id': row[0],
                'start_date': row[1],
                'car_type': row[2],
                'car_model': row[3],
                'problem_description': row[4],
                'request_status': row[5],
                'client_name': row[6],
                'master_name': row[7]
            }
        })
    return jsonify({'success': False, 'error': 'Not found'}), 404

@app.route('/api/users', methods=['GET'])
def get_users():
    """Получить всех пользователей."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, fio, phone, login, type FROM users')
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify({
        'success': True,
        'count': len(rows),
        'users': [
            {'user_id': row[0], 'fio': row[1], 'phone': row[2], 'login': row[3], 'type': row[4]}
            for row in rows
        ]
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Получить статистику."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Всего заявок
    cursor.execute('SELECT COUNT(*) FROM requests')
    total = cursor.fetchone()[0]
    
    # По статусам
    cursor.execute('SELECT request_status, COUNT(*) FROM requests GROUP BY request_status')
    by_status = dict(cursor.fetchall())
    
    # Среднее время ремонта
    cursor.execute('''
        SELECT AVG(julianday(completion_date) - julianday(start_date))
        FROM requests WHERE completion_date IS NOT NULL
    ''')
    avg_time = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': {
            'total_requests': total,
            'by_status': by_status,
            'avg_repair_days': round(avg_time, 2) if avg_time else 0
        }
    })
# В api.py добавьте:
@app.route('/api/requests', methods=['POST'])
def create_request():
    data = request.json
    # Валидация и вставка в БД
    return jsonify({'success': True, 'request_id': new_id}), 201

if __name__ == '__main__':
    print("🚀 Запуск API сервера на http://localhost:5000")
    app.run(debug=True, port=5000, host='127.0.0.1')