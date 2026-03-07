# forms/login_form.py
"""Форма авторизации пользователя."""
import tkinter as tk
from tkinter import messagebox
from database import get_connection


class LoginForm:
    """Форма авторизации пользователя."""
    
    def __init__(self, root, on_login_success):
        """
        Инициализация формы авторизации.
        
        Args:
            root: Корневое окно Tkinter
            on_login_success: Функция обратного вызова при успешной авторизации
        """
        self.root = root
        self.on_login_success = on_login_success
        
        self.root.title("Авторизация — Автосервис АвтоТранс")
        self.root.geometry("450x350")
        self.root.resizable(True, True)  # ✅ РАЗРЕШИТЬ изменение размера!
        self.root.configure(bg='#f5f6fa')
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Создать элементы интерфейса."""
        # Заголовок
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="🔧 Автосервис «АвтоТранс»",
            font=("Arial", 16, "bold"),
            bg='#2c3e50',
            fg='white'
        ).pack(pady=25)
        
        # Форма входа
        form_frame = tk.Frame(self.root, bg='#f5f6fa')
        form_frame.pack(pady=30, padx=40, fill=tk.X)
        
        # Логин
        tk.Label(
            form_frame,
            text="Логин:",
            font=("Arial", 11),
            bg='#f5f6fa'
        ).grid(row=0, column=0, sticky='w', pady=10)
        
        self.login_entry = tk.Entry(
            form_frame,
            width=30,
            font=("Arial", 11),
            bd=2,
            relief=tk.SOLID
        )
        self.login_entry.grid(row=0, column=1, pady=10, padx=10)
        self.login_entry.focus()
        
        # Пароль
        tk.Label(
            form_frame,
            text="Пароль:",
            font=("Arial", 11),
            bg='#f5f6fa'
        ).grid(row=1, column=0, sticky='w', pady=10)
        
        self.password_entry = tk.Entry(
            form_frame,
            width=30,
            font=("Arial", 11),
            show="•",
            bd=2,
            relief=tk.SOLID
        )
        self.password_entry.grid(row=1, column=1, pady=10, padx=10)
        self.password_entry.bind('<Return>', lambda e: self._authenticate())
        
        # Кнопка входа
        tk.Button(
            self.root,
            text="Войти в систему",
            command=self._authenticate,
            width=25,
            height=2,
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="white",
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        ).pack(pady=20)
        
        # Подсказка
        tk.Label(
            self.root,
            text="Пример: login1 / pass1 (Менеджер)",
            font=("Arial", 9),
            bg='#f5f6fa',
            fg="#7f8c8d"
        ).pack()
    
    def _authenticate(self):
        """Проверить учётные данные пользователя."""
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not login or not password:
            messagebox.showwarning(
                "Внимание",
                "Введите логин и пароль",
                parent=self.root
            )
            return
        
        try:
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
                    "Неверный логин или пароль.\nПроверьте введённые данные.",
                    parent=self.root
                )
        except Exception as e:
            messagebox.showerror(
                "Ошибка базы данных",
                f"Не удалось выполнить авторизацию:\n{e}",
                parent=self.root
            )