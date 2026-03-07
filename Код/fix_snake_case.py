# fix_snake_case.py
"""Скрипт для поиска нарушений snake_case в проекте."""

import re
from pathlib import Path
def main():
    project_root = Path(__file__).parent
    python_files = list(project_root.rglob("*.py"))
    
    # ✅ Исключаем системные файлы и виртуальное окружение
    exclude_patterns = [
        '__pycache__',
        '.venv',
        'venv',
        'env',
        'get-pip.py',
        'site-packages',
        'dist-packages',
    ]
    
    python_files = [
        f for f in python_files 
        if not any(excl in str(f) for excl in exclude_patterns)
    ]
    
def is_snake_case(name):
    """Проверить, что имя в snake_case."""
    # Разрешаем: маленькие буквы, цифры, подчёркивания
    return bool(re.match(r'^[a-z][a-z0-9_]*$', name)) or name.startswith('_')

def find_violations(file_path):
    """Найти нарушения snake_case в файле."""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            # Пропускаем комментарии и строки
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                continue
            
            # Поиск определений функций: def FunctionName(
            func_match = re.search(r'def\s+([A-Z][a-zA-Z0-9_]*)\s*\(', line)
            if func_match:
                func_name = func_match.group(1)
                if not is_snake_case(func_name):
                    violations.append({
                        'file': file_path,
                        'line': line_num,
                        'type': 'function',
                        'name': func_name,
                        'suggestion': ''.join(['_' + c.lower() if c.isupper() else c for c in func_name]).lstrip('_')
                    })
            
            # Поиск переменных в присваиваниях (простой паттерн)
            # Ищем: VariableName = (но не внутри функций/классов)
            var_match = re.search(r'^(\s*)([A-Z][a-zA-Z0-9_]*)\s*=', line)
            if var_match and 'def ' not in line and 'class ' not in line:
                var_name = var_match.group(2)
                # Пропускаем константы (UPPER_CASE) и классы
                if var_name.isupper() or var_name[0].isupper() and len(var_name) > 1 and var_name[1].isupper():
                    continue  # Это константа или класс
                if not is_snake_case(var_name):
                    violations.append({
                        'file': file_path,
                        'line': line_num,
                        'type': 'variable',
                        'name': var_name,
                        'suggestion': ''.join(['_' + c.lower() if c.isupper() else c for c in var_name]).lstrip('_')
                    })
                    
    except Exception as e:
        print(f"⚠️  Ошибка чтения {file_path}: {e}")
    
    return violations

def main():
    project_root = Path(__file__).parent
    python_files = list(project_root.rglob("*.py"))
    
    print("=" * 70)
    print("🔍 ПОИСК НАРУШЕНИЙ snake_case")
    print("=" * 70)
    
    all_violations = []
    
    for py_file in python_files:
        if "__pycache__" in str(py_file):
            continue
        
        violations = find_violations(py_file)
        if violations:
            print(f"\n📄 {py_file.relative_to(project_root)}:")
            for v in violations:
                print(f"   ❌ Строка {v['line']}: {v['type']} '{v['name']}' → '{v['suggestion']}'")
            all_violations.extend(violations)
    
    print("\n" + "=" * 70)
    print(f"📊 Всего нарушений: {len(all_violations)}")
    print("=" * 70)
    
    if all_violations:
        print("\n💡 Как исправить:")
        print("1. Откройте файл в редакторе")
        print("2. Найдите строку по номеру")
        print("3. Замените имя на предложенное")
        print("4. Не забудьте заменить ВСЕ использования этого имени в файле!")
    
    # Сохранить отчёт
    if all_violations:
        report_path = project_root / "snake_case_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("ОТЧЁТ: Нарушения snake_case\n")
            f.write("=" * 70 + "\n\n")
            for v in all_violations:
                f.write(f"Файл: {v['file'].relative_to(project_root)}\n")
                f.write(f"Строка: {v['line']}\n")
                f.write(f"Тип: {v['type']}\n")
                f.write(f"Было: {v['name']}\n")
                f.write(f"Стало: {v['suggestion']}\n")
                f.write("-" * 40 + "\n")
        print(f"\n✅ Отчёт сохранён: {report_path}")

if __name__ == "__main__":
    main()