# check_project.py
"""
Комплексная проверка проекта "Автосервис АвтоТранс"
Проверяет структуру, зависимости, БД, функциональность и соответствие ТЗ
"""

import sys
import os
import re
from pathlib import Path
from datetime import datetime

print("=" * 60)
print("🔍 ПРОВЕРКА ПРОЕКТА АВТОСЕРВИС АВТОТРАНС")
print("Вариант: В3_КОД 09.02.07-2-2024-ПУ")
print("=" * 60)

# Счетчики
passed = 0
failed = 0
warnings = 0

def test_section(name):
    """Вывод заголовка раздела"""
    print(f"\n{'='*60}")
    print(f"📋 {name}")
    print("=" * 60)

def check_passed(msg):
    global passed
    print(f"✅ {msg}")
    passed += 1

def check_failed(msg):
    global failed
    print(f"❌ {msg}")
    failed += 1

def check_warning(msg):
    global warnings
    print(f"⚠️  {msg}")
    warnings += 1

# ============================================
# 1. ПРОВЕРКА СТРУКТУРЫ ПРОЕКТА
# ============================================
test_section("1. СТРУКТУРА ПРОЕКТА")

project_root = Path(__file__).parent

# Основные файлы
required_files = [
    "main.py",
    "database.py",
    "requirements.txt",
    "forms/__init__.py",
    "forms/login_form.py",
    "forms/main_form.py",
    "forms/requests_form.py",
    "forms/users_form.py",
    "forms/reports_form.py",
    "utils/__init__.py",
    "utils/qr_generator.py",
    "utils/notifications.py",
    "utils/import_data.py",
]

for file_path in required_files:
    full_path = project_root / file_path
    if full_path.exists():
        check_passed(f"Файл существует: {file_path}")
    else:
        check_failed(f"Файл отсутствует: {file_path}")

# Папка data
data_dir = project_root / "data"
if data_dir.exists():
    check_passed("Папка data существует")
    if (data_dir / "auto_service.db").exists():
        check_passed("База данных auto_service.db существует")
    else:
        check_warning("База данных не найдена (будет создана при первом запуске)")
    
    # Проверка папки QR-кодов
    qr_dir = data_dir / "qr_codes"
    if qr_dir.exists():
        check_passed("Папка для QR-кодов существует")
    else:
        check_warning("Папка для QR-кодов будет создана при генерации")
else:
    check_warning("Папка data не найдена (будет создана автоматически)")

# ============================================
# 2. ПРОВЕРКА ЗАВИСИМОСТЕЙ
# ============================================
test_section("2. ПРОВЕРКА ЗАВИСИМОСТЕЙ")

dependencies = {
    "tkinter": "tkinter",
    "PIL": "Pillow",
    "qrcode": "qrcode",
}

for module, package_name in dependencies.items():
    try:
        __import__(module)
        check_passed(f"Модуль {package_name} установлен")
    except ImportError:
        check_failed(f"Модуль {package_name} НЕ установлен!")
        print(f"   Установите: pip install {package_name}")

# ============================================
# 3. ПРОВЕРКА БАЗЫ ДАННЫХ
# ============================================
test_section("3. ПРОВЕРКА БАЗЫ ДАННЫХ")

try:
    from database import get_connection, initialize_database
    
    check_passed("Модуль database.py импортируется")
    
    try:
        conn = get_connection()
        check_passed("Подключение к БД успешно")
        
        cursor = conn.cursor()
        
        # Проверка таблиц
        required_tables = ["users", "requests", "comments", "quality_surveys"]
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        for table in required_tables:
            if table in existing_tables:
                check_passed(f"Таблица '{table}' существует")
                
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                if columns:
                    check_passed(f"  └─ {len(columns)} колонок")
                    
                    # Проверка первичного ключа
                    pk_columns = [col for col in columns if col[5] == 1]
                    if pk_columns:
                        check_passed(f"  └─ Первичный ключ: {pk_columns[0][1]}")
                    else:
                        check_warning(f"  └─ Нет первичного ключа")
                else:
                    check_warning(f"  └─ Таблица '{table}' пустая")
            else:
                check_failed(f"Таблица '{table}' НЕ найдена!")
        
        # Проверка данных
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        if users_count > 0:
            check_passed(f"В таблице users {users_count} записей")
            
            # Проверка ролей
            cursor.execute("SELECT DISTINCT type FROM users")
            roles = [row[0] for row in cursor.fetchall()]
            check_passed(f"  └─ Ролей в системе: {len(roles)}")
            print(f"  └─ Роли: {', '.join(roles)}")
        else:
            check_warning("Таблица users пустая (нужно импортировать данные)")
        
        cursor.execute("SELECT COUNT(*) FROM requests")
        requests_count = cursor.fetchone()[0]
        if requests_count > 0:
            check_passed(f"В таблице requests {requests_count} записей")
        else:
            check_warning("Таблица requests пустая (нужно импортировать данные)")
        
        cursor.execute("SELECT COUNT(*) FROM comments")
        comments_count = cursor.fetchone()[0]
        check_passed(f"В таблице comments {comments_count} записей")
        
        conn.close()
        check_passed("Подключение к БД закрыто корректно")
        
    except Exception as e:
        check_failed(f"Ошибка подключения к БД: {e}")
        
except ImportError as e:
    check_failed(f"Не удалось импортировать database.py: {e}")

# ============================================
# 4. ПРОВЕРКА ФОРМ
# ============================================
test_section("4. ПРОВЕРКА МОДУЛЕЙ ФОРМ")

forms_to_check = [
    ("forms.login_form", "LoginForm", "Авторизация"),
    ("forms.main_form", "MainForm", "Главное меню"),
    ("forms.requests_form", "RequestsForm", "Заявки"),
    ("forms.users_form", "UsersForm", "Пользователи"),
    ("forms.reports_form", "ReportsForm", "Отчёты"),
]

for module_name, class_name, description in forms_to_check:
    try:
        module = __import__(module_name, fromlist=[class_name])
        if hasattr(module, class_name):
            check_passed(f"{description}: {class_name} найдена")
            
            # Проверка наличия ключевых методов
            cls = getattr(module, class_name)
            required_methods = ["__init__", "_create_widgets"]
            for method in required_methods:
                if hasattr(cls, method):
                    check_passed(f"  └─ Метод {method}() существует")
                else:
                    check_warning(f"  └─ Метод {method}() не найден")
        else:
            check_failed(f"Класс {class_name} не найден в {module_name}")
    except Exception as e:
        check_failed(f"Ошибка импорта {module_name}: {e}")

# ============================================
# 5. ПРОВЕРКА ФУНКЦИОНАЛЬНОСТИ (по протоколу)
# ============================================
test_section("5. ФУНКЦИОНАЛЬНЫЕ ПРОВЕРКИ (по протоколу)")

# TC_AUTH_001: Авторизация
try:
    from forms.login_form import LoginForm
    check_passed("TC_AUTH_001: Модуль авторизации существует")
except:
    check_failed("TC_AUTH_001: Модуль авторизации НЕ найден")

# TC_REQ_001: Просмотр заявок
try:
    from forms.requests_form import RequestsForm
    check_passed("TC_REQ_001: Модуль заявок существует")
except:
    check_failed("TC_REQ_001: Модуль заявок НЕ найден")

# TC_REQ_002: Добавление заявки
try:
    with open(project_root / "forms" / "requests_form.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "_add_request" in content:
            check_passed("TC_REQ_002: Функция добавления заявки реализована")
        else:
            check_failed("TC_REQ_002: Функция добавления заявки НЕ найдена")
except:
    check_failed("TC_REQ_002: Ошибка проверки")

# TC_REQ_003: Редактирование статуса
try:
    with open(project_root / "forms" / "requests_form.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "_edit_request" in content and "request_status" in content:
            check_passed("TC_REQ_003: Редактирование статуса реализовано")
        else:
            check_failed("TC_REQ_003: Редактирование статуса НЕ найдено")
except:
    check_failed("TC_REQ_003: Ошибка проверки")

# TC_REQ_004: Поиск заявок
try:
    with open(project_root / "forms" / "requests_form.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "_search_requests" in content:
            check_passed("TC_REQ_004: Поиск заявок реализован")
        else:
            check_failed("TC_REQ_004: Поиск заявок НЕ найден")
except:
    check_failed("TC_REQ_004: Ошибка проверки")

# TC_REQ_005: Фильтр по статусу
try:
    with open(project_root / "forms" / "requests_form.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "_filter_by_status" in content:
            check_passed("TC_REQ_005: Фильтр по статусу реализован")
        else:
            check_failed("TC_REQ_005: Фильтр по статусу НЕ найден")
except:
    check_failed("TC_REQ_005: Ошибка проверки")

# TC_REQ_006: Назначение механика
try:
    with open(project_root / "forms" / "requests_form.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "master_id" in content or "Мастер" in content:
            check_passed("TC_REQ_006: Назначение механика реализовано")
        else:
            check_failed("TC_REQ_006: Назначение механика НЕ найдено")
except:
    check_failed("TC_REQ_006: Ошибка проверки")

# TC_REP_001: Статистика
try:
    from forms.reports_form import ReportsForm
    check_passed("TC_REP_001: Модуль отчётов существует")
except:
    check_failed("TC_REP_001: Модуль отчётов НЕ найден")

# TC_QR_001: QR-код
try:
    from utils.qr_generator import generate_qr_code
    check_passed("TC_QR_001: Генерация QR-кода реализована")
except:
    check_failed("TC_QR_001: Генерация QR-кода НЕ найдена")

# TC_USR_001: Фильтр пользователей
try:
    with open(project_root / "forms" / "users_form.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "_filter_users" in content or "_filter_by_role" in content:
            check_passed("TC_USR_001: Фильтр пользователей реализован")
        else:
            check_failed("TC_USR_001: Фильтр пользователей НЕ найден")
except:
    check_failed("TC_USR_001: Ошибка проверки")

# TC_VAL_001: Валидация
try:
    with open(project_root / "forms" / "requests_form.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "messagebox.showwarning" in content or "messagebox.showerror" in content:
            check_passed("TC_VAL_001: Валидация ввода реализована")
        else:
            check_failed("TC_VAL_001: Валидация ввода НЕ найдена")
except:
    check_failed("TC_VAL_001: Ошибка проверки")

# TC_ERR_001: Обработка ошибок
try:
    with open(project_root / "forms" / "requests_form.py", "r", encoding="utf-8") as f:
        content = f.read()
        if "try:" in content and "except" in content:
            check_passed("TC_ERR_001: Обработка исключений реализована")
        else:
            check_failed("TC_ERR_001: Обработка исключений НЕ найдена")
except:
    check_failed("TC_ERR_001: Ошибка проверки")
# ============================================
# 6. КАЧЕСТВО КОДА (гайдлайн)
# ============================================
test_section("6. КАЧЕСТВО КОДА (гайдлайн)")

# ✅ Получаем список ВСЕХ Python-файлов проекта
all_python_files = list(project_root.rglob("*.py"))

# ✅ Фильтруем: проверяем ТОЛЬКО ваши файлы (исключаем .venv, __pycache__, системные)
your_files = []
for py_file in all_python_files:
    file_str = str(py_file)
    if any(excl in file_str for excl in [
        '__pycache__', '.venv', 'get-pip.py', 
        'site-packages', 'dist-packages', 'venv'
    ]):
        continue
    your_files.append(py_file)

# ✅ Проверка snake_case только в ваших файлах
snake_case_violations = 0
for py_file in your_files:  # ← Используем your_files, а не python_files
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Ищем функции: def FunctionName( (CamelCase — нарушение)
            func_pattern = r'def\s+([A-Z][a-zA-Z0-9_]*)\s*\('
            violations = re.findall(func_pattern, content)
            snake_case_violations += len(violations)
    except Exception as e:
        pass  # Игнорируем ошибки чтения

# ✅ Вывод результата
if snake_case_violations == 0:
    check_passed("snake_case: Нарушений в ВАШЕМ коде не найдено ✅")
else:
    check_warning(f"snake_case: Найдено {snake_case_violations} нарушений")

# Проверка комментариев (docstring)
total_docstrings = 0
for py_file in your_files:  # ← Используем your_files
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            total_docstrings += content.count('"""')
    except:
        pass

if total_docstrings > 0:
    check_passed(f"Комментарии: Найдено {total_docstrings // 2} docstring-ов")
else:
    check_warning("Комментарии: Docstring-и не найдены")

# Проверка обработки исключений
exception_count = 0
for py_file in your_files:  # ← Используем your_files
    try:
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            exception_count += content.count("try:")
    except:
        pass

if exception_count > 0:
    check_passed(f"Обработка ошибок: Найдено {exception_count} блоков try/except")
else:
    check_failed("Обработка ошибок: Блоки try/except не найдены")

# ============================================
# 7. ПРОВЕРКА CSV ФАЙЛОВ
# ============================================
test_section("7. ПРОВЕРКА CSV ФАЙЛОВ")

csv_files = [
    "inputDataUsers.csv",
    "inputDataRequests.csv",
    "inputDataComments.csv",
]

for csv_file in csv_files:
    possible_paths = [
        project_root / csv_file,
        project_root.parent / csv_file,
        project_root / "data" / "imports" / csv_file,
    ]
    
    found = False
    for path in possible_paths:
        if path.exists():
            check_passed(f"CSV файл найден: {csv_file}")
            
            # Проверка размера файла
            size = path.stat().st_size
            if size > 0:
                check_passed(f"  └─ Размер: {size} байт")
            else:
                check_warning(f"  └─ Файл пустой")
            
            found = True
            break
    
    if not found:
        check_warning(f"CSV файл не найден: {csv_file}")

# ============================================
# 8. СООТВЕТСТВИЕ ТРЕБОВАНИЯМ ТЗ
# ============================================
test_section("8. СООТВЕТСТВИЕ ТРЕБОВАНИЯМ ТЗ")

# ✅ Используем your_files (определён в разделе 6)
requirements = {
    "2.1 Добавление заявок": ["request_id", "start_date", "car_type", "car_model", "problem_description", "request_status", "client_id"],
    "2.2 Редактирование": ["UPDATE", "request_status", "master_id"],
    "2.3 Отслеживание статуса": ["SELECT", "request_status", "search"],
    "2.4 Назначение ответственных": ["master_id", "comments"],
    "2.5 Статистика": ["COUNT", "AVG", "GROUP BY"],
    "3.2 Безопасность": ["login", "password", "type"],
}

for req, keywords in requirements.items():
    found_keywords = 0
    for py_file in your_files:  # ← Используем your_files, а не python_files
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read().upper()
                for keyword in keywords:
                    if keyword.upper() in content:
                        found_keywords += 1
        except:
            pass
    
    if found_keywords >= len(keywords) * 0.5:
        check_passed(f"{req}: Реализовано ({found_keywords}/{len(keywords)})")
    else:
        check_warning(f"{req}: Частично реализовано ({found_keywords}/{len(keywords)})")

# ============================================
# 9. ПРОВЕРКА ВЕРСИИ PYTHON
# ============================================
test_section("9. ВЕРСИЯ PYTHON")

python_version = sys.version_info
print(f"Версия Python: {python_version.major}.{python_version.minor}.{python_version.micro}")

if python_version.major == 3 and python_version.minor >= 8:
    check_passed("Версия Python соответствует требованиям (>= 3.8)")
else:
    check_failed("Требуется Python 3.8 или выше!")

# ============================================
# 10. ПРОВЕРКА ПУТЕЙ
# ============================================
test_section("10. ПРОВЕРКА ПУТЕЙ")

print(f"Корень проекта: {project_root}")
print(f"Текущая директория: {Path.cwd()}")

if project_root.exists():
    check_passed("Путь к проекту корректен")
else:
    check_failed("Путь к проекту не существует!")

# ============================================
# 11. ПРОВЕРКА РЕЗЕРВНОГО КОПИРОВАНИЯ
# ============================================
test_section("11. РЕЗЕРВНОЕ КОПИРОВАНИЕ")

backup_dir = project_root / "backups"
if backup_dir.exists():
    check_passed("Папка для резервных копий существует")
    backup_files = list(backup_dir.glob("*.db")) + list(backup_dir.glob("*.sql"))
    if backup_files:
        check_passed(f"Найдено {len(backup_files)} резервных копий")
    else:
        check_warning("Резервные копии не найдены (рекомендуется создать)")
else:
    check_warning("Папка для резервных копий не найдена")

# ============================================
# ИТОГОВЫЙ ОТЧЕТ
# ============================================
print("\n" + "=" * 60)
print("📊 ИТОГОВЫЙ ОТЧЕТ")
print("=" * 60)
print(f"✅ Пройдено проверок: {passed}")
print(f"❌ Ошибок: {failed}")
print(f"⚠️  Предупреждений: {warnings}")
print("=" * 60)

total_checks = passed + failed
if total_checks > 0:
    success_rate = (passed / total_checks) * 100
    print(f"📈 Процент успешных проверок: {success_rate:.1f}%")

print("=" * 60)

if failed == 0:
    print("\n🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
    print("Проект готов к демонстрационному экзамену!")
    print("\nДля запуска выполните:")
    print("  py -3.14 main.py")
else:
    print(f"\n⚠️  Обнаружено {failed} ошибок!")
    print("Устраните ошибки перед запуском.")
    
    if warnings > 0:
        print(f"\n⚠️  Также есть {warnings} предупреждений.")
        print("Рекомендуется их устранить.")

print("=" * 60 + "\n")

# Сохранение отчета
report_path = project_root / "check_report.txt"
try:
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"ОТЧЕТ ПРОВЕРКИ ПРОЕКТА\n")
        f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"=" * 60 + "\n")
        f.write(f"✅ Пройдено: {passed}\n")
        f.write(f"❌ Ошибок: {failed}\n")
        f.write(f"⚠️  Предупреждений: {warnings}\n")
        if total_checks > 0:
            f.write(f"📈 Успешность: {success_rate:.1f}%\n")
        f.write(f"=" * 60 + "\n")
    check_passed(f"Отчет сохранен: {report_path}")
except:
    check_warning("Не удалось сохранить отчет")