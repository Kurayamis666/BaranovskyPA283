# forms/login_form.py
"""Форма авторизации пользователя."""
import tkinter as tk
from tkinter import messagebox
from database import get_connection


class LoginForm:
    """Форма авторизации пользователя."""
    
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.root.geometry("420x320")
        self.root.resizable(False, False)
        self._create_widgets()
    
    def _create_widgets(self):
        """Создать элементы интерфейса."""
        # Заголовок
        title = tk.Label(
            self.root,
            text="🔧 Автосервис «АвтоТранс»",
            font=("Arial", 16, "bold"),
            fg="#2c3e50"
        )
        title.pack(pady=25)
        
        # Форма входа
        form_frame = tk.Frame(self.root)
        form_frame.pack(pady=10)
        
        tk.Label(form_frame, text="Логин:", font=("Arial", 11)).grid(row=0, column=0, sticky='e', padx=10, pady=5)
        self.login_entry = tk.Entry(form_frame, width=30, font=("Arial", 11))
        self.login_entry.grid(row=0, column=1, padx=10, pady=5)
        self.login_entry.focus()
        
        tk.Label(form_frame, text="Пароль:", font=("Arial", 11)).grid(row=1, column=0, sticky='e', padx=10, pady=5)
        self.password_entry = tk.Entry(form_frame, width=30, show="•", font=("Arial", 11))
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)
        self.password_entry.bind('<Return>', lambda e: self._authenticate())
        
        # Кнопка входа
        login_btn = tk.Button(
            self.root,
            text="Войти в систему",
            command=self._authenticate,
            width=25,
            height=2,
            bg="#3498db",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2"
        )
        login_btn.pack(pady=20)
        
        # Подсказка
        hint = tk.Label(
            self.root,
            text="Пример: login1 / pass1 (Менеджер)",
            font=("Arial", 9),
            fg="#7f8c8d"
        )
        hint.pack()
    
    def _authenticate(self):
        """Проверить учётные данные пользователя."""
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not login or not password:
            messagebox.showwarning("Внимание", "Введите логин и пароль")
            return
        
        connection = get_connection()
        cursor = connection.cursor()
        
        cursor.execute(
            "SELECT user_id, fio, type FROM users WHERE login = ? AND password = ?",
            (login, password)
        )
        user = cursor.fetchone()
        connection.close()
        
        if user:
            user_data = {
                'user_id': user['user_id'],
                'fio': user['fio'],
                'type': user['type']
            }
            self.on_login_success(user_data)
        else:
            messagebox.showerror(
                "Ошибка авторизации",
                "Неверный логин или пароль.\nПроверьте введённые данные."
            )