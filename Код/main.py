# main.py
"""Точка входа приложения Автосервис АвтоТранс."""
import tkinter as tk
from pathlib import Path
import shutil
from datetime import datetime
from database import initialize_database
from forms.login_form import LoginForm

def auto_backup():
    """Автоматический backup при запуске."""
    try:
        project_root = Path(__file__).parent
        db_path = project_root / "data" / "auto_service.db"
        backup_dir = project_root / "backups"
        
        if db_path.exists():
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d")
            backup_path = backup_dir / f"auto_daily_backup_{timestamp}.db"
            
            # Копируем только если сегодня ещё не было backup
            if not backup_path.exists():
                shutil.copy2(db_path, backup_path)
                print(f"✅ Автоматический backup создан: {backup_path.name}")
    except Exception as e:
        print(f"⚠️  Ошибка автоматического backup: {e}")

def on_login_success(user_data, login_window):
    """
    Обработчик успешной авторизации.
    
    Args:
        user_data: Данные пользователя
        login_window: Окно авторизации
    """
    login_window.withdraw()  # Скрываем окно авторизации
    
    from forms.main_form import MainForm
    main_window = tk.Tk()
    MainForm(main_window, user_data, login_window)  # ✅ Передаем login_window
    main_window.mainloop()


def main():
    """Основная функция приложения."""
    # Инициализация базы данных
    initialize_database()
    
    # Создание окна авторизации
    root = tk.Tk()
    LoginForm(root, lambda user_data: on_login_success(user_data, root))
    root.mainloop()


if __name__ == "__main__":
    main()