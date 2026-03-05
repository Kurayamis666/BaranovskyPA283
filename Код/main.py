# main.py
"""Точка входа приложения Автосервис АвтоТранс."""
import tkinter as tk
from tkinter import messagebox
from database import initialize_database
from forms.login_form import LoginForm
from utils.import_data import import_all_data


def on_login_success(user_data):
    """Обработчик успешной авторизации."""
    login_window.destroy()
    from forms.main_form import MainForm
    main_window = tk.Tk()
    MainForm(main_window, user_data)
    main_window.mainloop()


def initial_data_import():
    """Импортировать данные при первом запуске."""
    result = import_all_data()
    if result['total_errors'] == 0:
        print(f"✅ Импорт завершён: {result['total_success']} записей")
    else:
        print(f"⚠️ Импорт: {result['total_success']} успешно, {result['total_errors']} ошибок")


if __name__ == "__main__":
    # Инициализация БД
    initialize_database()
    
    # Импорт данных (можно закомментировать после первого запуска)
    initial_data_import()
    
    # Запуск приложения
    login_window = tk.Tk()
    login_window.title("Авторизация — Автосервис АвтоТранс")
    LoginForm(login_window, on_login_success)
    login_window.mainloop()