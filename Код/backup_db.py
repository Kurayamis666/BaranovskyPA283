# backup_db.py
"""
Скрипт резервного копирования базы данных
Автосервис «АвтоТранс»
"""

import shutil
from pathlib import Path
from datetime import datetime
import os

def create_backup():
    """Создать резервную копию базы данных."""
    
    print("=" * 60)
    print("🗄️  РЕЗЕРВНОЕ КОПИРОВАНИЕ БАЗЫ ДАННЫХ")
    print("Автосервис «АвтоТранс»")
    print("=" * 60)
    
    # Пути
    project_root = Path(__file__).parent
    db_path = project_root / "data" / "auto_service.db"
    backup_dir = project_root / "backups"
    
    # Проверка существования БД
    if not db_path.exists():
        print(f"❌ База данных не найдена: {db_path}")
        return False
    
    print(f"✅ База данных найдена: {db_path}")
    print(f"   Размер: {db_path.stat().st_size} байт")
    
    # Создание папки для backup
    backup_dir.mkdir(exist_ok=True)
    print(f"✅ Папка для резервных копий: {backup_dir}")
    
    # Формирование имени файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"auto_service_backup_{timestamp}.db"
    backup_path = backup_dir / backup_filename
    
    try:
        # Копирование файла
        shutil.copy2(db_path, backup_path)
        
        print(f"\n✅ Резервная копия создана успешно!")
        print(f"   Файл: {backup_filename}")
        print(f"   Путь: {backup_path}")
        print(f"   Размер: {backup_path.stat().st_size} байт")
        
        # Проверка целостности
        if backup_path.exists():
            print(f"\n✅ Проверка целостности: Файл существует")
        else:
            print(f"\n❌ Проверка целостности: Файл не создан!")
            return False
        
        # Очистка старых бэкапов (храним последние 10)
        cleanup_old_backups(backup_dir, keep_count=10)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка создания резервной копии: {e}")
        return False

def cleanup_old_backups(backup_dir, keep_count=10):
    """Удалить старые резервные копии, оставив последние keep_count штук."""
    
    try:
        # Получаем список всех backup файлов
        backup_files = sorted(
            backup_dir.glob("auto_service_backup_*.db"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        # Удаляем старые, если их больше keep_count
        if len(backup_files) > keep_count:
            print(f"\n🗑️  Очистка старых резервных копий...")
            for old_file in backup_files[keep_count:]:
                old_file.unlink()
                print(f"   Удалено: {old_file.name}")
            
            print(f"   Оставлено последних: {keep_count}")
        
    except Exception as e:
        print(f"⚠️  Ошибка очистки старых бэкапов: {e}")

def list_backups():
    """Показать список всех резервных копий."""
    
    project_root = Path(__file__).parent
    backup_dir = project_root / "backups"
    
    print("\n" + "=" * 60)
    print("📋 СПИСОК РЕЗЕРВНЫХ КОПИЙ")
    print("=" * 60)
    
    if not backup_dir.exists():
        print("❌ Папка backups не найдена")
        return
    
    backup_files = sorted(
        backup_dir.glob("auto_service_backup_*.db"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    if not backup_files:
        print("⚠️  Резервные копии не найдены")
        return
    
    print(f"\nВсего копий: {len(backup_files)}\n")
    
    for i, file in enumerate(backup_files, 1):
        size = file.stat().st_size
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        print(f"{i}. {file.name}")
        print(f"   Дата: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Размер: {size:,} байт")
        print()

def restore_backup(backup_filename=None):
    """Восстановить базу данных из резервной копии."""
    
    project_root = Path(__file__).parent
    db_path = project_root / "data" / "auto_service.db"
    backup_dir = project_root / "backups"
    
    print("\n" + "=" * 60)
    print("♻️  ВОССТАНОВЛЕНИЕ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    # Проверка папки backup
    if not backup_dir.exists():
        print("❌ Папка backups не найдена")
        return False
    
    # Поиск файла backup
    if backup_filename:
        backup_path = backup_dir / backup_filename
        if not backup_path.exists():
            print(f"❌ Файл не найден: {backup_filename}")
            return False
    else:
        # Берем последнюю копию
        backup_files = sorted(
            backup_dir.glob("auto_service_backup_*.db"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        if not backup_files:
            print("❌ Резервные копии не найдены")
            return False
        backup_path = backup_files[0]
        print(f"Используется последняя копия: {backup_path.name}")
    
    # Создание папки data если нет
    db_path.parent.mkdir(exist_ok=True)
    
    try:
        # Копирование backup в data
        shutil.copy2(backup_path, db_path)
        print(f"\n✅ База данных восстановлена успешно!")
        print(f"   Из файла: {backup_path.name}")
        print(f"   В файл: {db_path}")
        return True
    except Exception as e:
        print(f"\n❌ Ошибка восстановления: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "backup":
            create_backup()
        elif command == "list":
            list_backups()
        elif command == "restore":
            backup_file = sys.argv[2] if len(sys.argv) > 2 else None
            restore_backup(backup_file)
        else:
            print("Неизвестная команда. Доступные команды:")
            print("  backup  - создать резервную копию")
            print("  list    - показать список копий")
            print("  restore - восстановить из последней копии")
            print("  restore <filename> - восстановить из конкретного файла")
    else:
        # По умолчанию создаем backup
        create_backup()