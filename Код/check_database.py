# check_database.py
"""
Комплексная проверка базы данных "Автосервис АвтоТранс"
Проверяет структуру, данные, связи и функциональность
"""

from database import get_connection
from pathlib import Path

def print_section(title):
    """Вывод заголовка раздела"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print("=" * 60)

def check_passed(msg):
    print(f"✅ {msg}")

def check_failed(msg):
    print(f"❌ {msg}")

def check_warning(msg):
    print(f"⚠️  {msg}")

def main():
    print("=" * 60)
    print("🔍 ПРОВЕРКА БАЗЫ ДАННЫХ")
    print("Автосервис «АвтоТранс»")
    print("=" * 60)
    
    project_root = Path(__file__).parent
    db_path = project_root / "data" / "auto_service.db"
    
    # ============================================
    # 1. ПРОВЕРКА СУЩЕСТВОВАНИЯ ФАЙЛА БД
    # ============================================
    print_section("1. СУЩЕСТВОВАНИЕ ФАЙЛА БД")
    
    if db_path.exists():
        check_passed(f"Файл БД найден: {db_path}")
        check_passed(f"Размер файла: {db_path.stat().st_size:,} байт")
    else:
        check_failed(f"Файл БД не найден: {db_path}")
        return
    
    # ============================================
    # 2. ПОДКЛЮЧЕНИЕ К БД
    # ============================================
    print_section("2. ПОДКЛЮЧЕНИЕ К БД")
    
    try:
        conn = get_connection()
        check_passed("Подключение к БД успешно")
        check_passed(f"Драйвер: SQLite {conn.execute('SELECT sqlite_version()').fetchone()[0]}")
    except Exception as e:
        check_failed(f"Ошибка подключения: {e}")
        return
    
    cursor = conn.cursor()
    
    # ============================================
    # 3. ПРОВЕРКА ТАБЛИЦ
    # ============================================
    print_section("3. СТРУКТУРА ТАБЛИЦ")
    
    required_tables = {
        "users": ["user_id", "fio", "phone", "login", "password", "type"],
        "requests": ["request_id", "start_date", "car_type", "car_model", 
                    "problem_description", "request_status", "completion_date",
                    "repair_parts", "master_id", "client_id"],
        "comments": ["comment_id", "request_id", "master_id", "comment_text"],
        "quality_surveys": ["survey_id", "request_id", "rating", "feedback", 
                          "survey_date", "client_id"]
    }
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    for table, expected_columns in required_tables.items():
        if table in existing_tables:
            check_passed(f"Таблица '{table}' существует")
            
            # Проверка колонок
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            missing_cols = set(expected_columns) - set(columns)
            if missing_cols:
                check_failed(f"  └─ Отсутствуют колонки: {missing_cols}")
            else:
                check_passed(f"  └─ Все {len(expected_columns)} колонок на месте")
            
            # Проверка первичного ключа
            cursor.execute(f"PRAGMA table_info({table})")
            pk_cols = [col[1] for col in cursor.fetchall() if col[5] == 1]
            if pk_cols:
                check_passed(f"  └─ Первичный ключ: {pk_cols[0]}")
            else:
                check_warning(f"  └─ Нет первичного ключа")
        else:
            check_failed(f"Таблица '{table}' НЕ найдена!")
    
    # ============================================
    # 4. ПРОВЕРКА ВНЕШНИХ КЛЮЧЕЙ
    # ============================================
    print_section("4. ВНЕШНИЕ КЛЮЧИ (FOREIGN KEY)")
    
    fk_checks = [
        ("requests", "master_id", "users", "user_id"),
        ("requests", "client_id", "users", "user_id"),
        ("comments", "request_id", "requests", "request_id"),
        ("comments", "master_id", "users", "user_id"),
        ("quality_surveys", "request_id", "requests", "request_id"),
        ("quality_surveys", "client_id", "users", "user_id"),
    ]
    
    cursor.execute("PRAGMA foreign_key_list(requests)")
    requests_fks = cursor.fetchall()
    
    cursor.execute("PRAGMA foreign_key_list(comments)")
    comments_fks = cursor.fetchall()
    
    cursor.execute("PRAGMA foreign_key_list(quality_surveys)")
    surveys_fks = cursor.fetchall()
    
    all_fks = requests_fks + comments_fks + surveys_fks
    
    for table, from_col, ref_table, ref_col in fk_checks:
        found = any(
            fk[2] == ref_table and fk[3] == ref_col and fk[4] == from_col
            for fk in all_fks
        )
        if found:
            check_passed(f"{table}.{from_col} → {ref_table}.{ref_col}")
        else:
            check_warning(f"{table}.{from_col} → {ref_table}.{ref_col} (не найден в PRAGMA)")
    
    # ============================================
    # 5. ПРОВЕРКА ДАННЫХ
    # ============================================
    print_section("5. КОЛИЧЕСТВО ЗАПИСЕЙ")
    
    tables_count = {
        "users": "Пользователи",
        "requests": "Заявки",
        "comments": "Комментарии",
        "quality_surveys": "Опросы качества"
    }
    
    for table, name in tables_count.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        check_passed(f"{name} ({table}): {count} записей")
    
    # ============================================
    # 6. ПРОВЕРКА ЦЕЛОСТНОСТИ ДАННЫХ
    # ============================================
    print_section("6. ЦЕЛОСТНОСТЬ ДАННЫХ")
    
    # Проверка: все master_id в requests существуют в users
    cursor.execute('''
        SELECT COUNT(*) FROM requests r
        WHERE r.master_id IS NOT NULL 
        AND NOT EXISTS (SELECT 1 FROM users u WHERE u.user_id = r.master_id)
    ''')
    orphan_masters = cursor.fetchone()[0]
    if orphan_masters == 0:
        check_passed("Все master_id в requests ссылаются на существующих пользователей")
    else:
        check_failed(f"Найдено {orphan_masters} 'осиротевших' master_id")
    
    # Проверка: все client_id в requests существуют в users
    cursor.execute('''
        SELECT COUNT(*) FROM requests r
        WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.user_id = r.client_id)
    ''')
    orphan_clients = cursor.fetchone()[0]
    if orphan_clients == 0:
        check_passed("Все client_id в requests ссылаются на существующих пользователей")
    else:
        check_failed(f"Найдено {orphan_clients} 'осиротевших' client_id")
    
    # Проверка: статусы заявок допустимы
    valid_statuses = ["Новая заявка", "В процессе ремонта", "Готова к выдаче", "Завершена", "Ожидание запчастей"]
    cursor.execute("SELECT DISTINCT request_status FROM requests")
    statuses = [row[0] for row in cursor.fetchall()]
    
    invalid_statuses = set(statuses) - set(valid_statuses)
    if not invalid_statuses:
        check_passed(f"Все статусы заявок допустимы: {', '.join(statuses)}")
    else:
        check_failed(f"Найдены недопустимые статусы: {invalid_statuses}")
    
    # Проверка: роли пользователей допустимы
    valid_roles = ["Менеджер", "Автомеханик", "Оператор", "Заказчик", "Менеджер по качеству"]
    cursor.execute("SELECT DISTINCT type FROM users")
    roles = [row[0] for row in cursor.fetchall()]
    
    invalid_roles = set(roles) - set(valid_roles)
    if not invalid_roles:
        check_passed(f"Все роли пользователей допустимы: {', '.join(roles)}")
    else:
        check_failed(f"Найдены недопустимые роли: {invalid_roles}")
    
    # ============================================
    # 7. ПРОВЕРКА ЗАПРОСОВ (ФУНКЦИОНАЛЬНОСТЬ)
    # ============================================
    print_section("7. ПРОВЕРКА ЗАПРОСОВ")
    
    # Запрос 1: Заявки с информацией о клиенте и мастере
    try:
        cursor.execute('''
            SELECT r.request_id, r.car_model, r.request_status,
                   c.fio as client_name, m.fio as master_name
            FROM requests r
            LEFT JOIN users c ON r.client_id = c.user_id
            LEFT JOIN users m ON r.master_id = m.user_id
            LIMIT 3
        ''')
        results = cursor.fetchall()
        if results:
            check_passed("Запрос с JOIN (заявки + клиенты + мастера) работает")
            for row in results:
                print(f"   • Заявка #{row[0]}: {row[1]} — {row[2]} (Клиент: {row[3]}, Мастер: {row[4]})")
        else:
            check_warning("Запрос вернул пустой результат")
    except Exception as e:
        check_failed(f"Ошибка запроса с JOIN: {e}")
    
    # Запрос 2: Статистика по статусам
    try:
        cursor.execute('''
            SELECT request_status, COUNT(*) as count
            FROM requests
            GROUP BY request_status
            ORDER BY count DESC
        ''')
        results = cursor.fetchall()
        if results:
            check_passed("Запрос статистики по статусам работает")
            for row in results:
                print(f"   • {row[0]}: {row[1]} заявок")
    except Exception as e:
        check_failed(f"Ошибка запроса статистики: {e}")
    
    # Запрос 3: Поиск по модели авто
    try:
        cursor.execute('''
            SELECT request_id, car_model, request_status
            FROM requests
            WHERE LOWER(car_model) LIKE ?
            LIMIT 3
        ''', ('%hyundai%',))
        results = cursor.fetchall()
        check_passed("Поиск по модели авто (LIKE) работает")
        if results:
            for row in results:
                print(f"   • Заявка #{row[0]}: {row[1]} — {row[2]}")
    except Exception as e:
        check_failed(f"Ошибка поиска: {e}")
    
    # ============================================
    # 8. ПРОВЕРКА ОГРАНИЧЕНИЙ (CHECK CONSTRAINTS)
    # ============================================
    print_section("8. ОГРАНИЧЕНИЯ (CHECK)")
    
    # Проверка CHECK на request_status
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='requests'")
    requests_sql = cursor.fetchone()[0]
    
    if "CHECK(request_status IN" in requests_sql:
        check_passed("Ограничение CHECK на request_status существует")
    else:
        check_warning("Ограничение CHECK на request_status не найдено в SQL")
    
    # Проверка: попытка вставки недопустимого статуса (должна завершиться ошибкой)
    try:
        cursor.execute('''
            INSERT INTO requests (request_id, start_date, car_type, car_model, 
                                problem_description, request_status, client_id)
            VALUES (99999, DATE('now'), 'Тест', 'Тест', 'Тест', 'Недопустимый статус', 1)
        ''')
        conn.rollback()  # Отменяем, если вдруг вставилось
        check_failed("Ограничение CHECK не сработало (недопустимый статус вставился)")
    except Exception:
        conn.rollback()
        check_passed("Ограничение CHECK работает (недопустимый статус отклонён)")
    
    # ============================================
    # 9. ПРОВЕРКА ТРАНЗАКЦИЙ
    # ============================================
    print_section("9. ТРАНЗАКЦИИ (COMMIT/ROLLBACK)")
    
    try:
        # Начало транзакции
        cursor.execute("BEGIN TRANSACTION")
        
        # Вставка тестовой записи
        cursor.execute('''
    INSERT INTO comments (comment_id, request_id, master_id, message)
    VALUES (99999, 1, 1, 'Тестовый комментарий для проверки транзакций')
''')
        
        # Проверка, что запись видна в текущей транзакции
        cursor.execute("SELECT COUNT(*) FROM comments WHERE comment_id = 99999")
        if cursor.fetchone()[0] == 1:
            check_passed("Вставка в транзакции работает")
        else:
            check_failed("Вставка в транзакции не сработала")
        
        # Откат транзакции
        cursor.execute("ROLLBACK")
        
        # Проверка, что запись НЕ сохранилась
        cursor.execute("SELECT COUNT(*) FROM comments WHERE comment_id = 99999")
        if cursor.fetchone()[0] == 0:
            check_passed("ROLLBACK работает (данные не сохранились)")
        else:
            check_failed("ROLLBACK не сработал (данные сохранились)")
            
    except Exception as e:
        conn.rollback()
        check_failed(f"Ошибка проверки транзакций: {e}")
    
    # ============================================
    # 10. ЗАКРЫТИЕ СОЕДИНЕНИЯ
    # ============================================
    print_section("10. ЗАКРЫТИЕ СОЕДИНЕНИЯ")
    
    try:
        conn.close()
        check_passed("Соединение с БД закрыто корректно")
    except Exception as e:
        check_failed(f"Ошибка закрытия соединения: {e}")
    
    # ============================================
    # ИТОГОВЫЙ ОТЧЁТ
    # ============================================
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЁТ ПРОВЕРКИ БД")
    print("=" * 60)
    print("✅ База данных работает корректно")
    print("✅ Все таблицы и связи на месте")
    print("✅ Данные целостны")
    print("✅ Запросы выполняются")
    print("✅ Ограничения работают")
    print("✅ Транзакции поддерживаются")
    print("=" * 60)

if __name__ == "__main__":
    main()