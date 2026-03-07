# forms/main_form.py
"""Главное окно приложения после авторизации."""
import tkinter as tk
from tkinter import messagebox
from .requests_form import RequestsForm
from .users_form import UsersForm
from .reports_form import ReportsForm


class MainForm:
    """Главное окно приложения."""
    
    def __init__(self, root, user_data, login_window=None):
        """
        Инициализация главного окна.
        
        Args:
            root: Корневое окно Tkinter
            user_data: Данные авторизованного пользователя
            login_window: Окно авторизации (для возврата)
        """
        self.root = root
        self.user_data = user_data
        self.login_window = login_window  # Сохраняем ссылку на окно авторизации
        
        self.root.title(f"Главное меню — {user_data['fio']}")
        self.root.geometry("800x600")
        self.root.resizable(False, False)  # ✅ РАЗРЕШИТЬ изменение размера!
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Создать элементы главного меню."""
        # Шапка
        header = tk.Frame(self.root, bg="#2c3e50", height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🔧 Автосервис «АвтоТранс»",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=30)
        
        # Информация о пользователе
        user_frame = tk.Frame(self.root, bg="#ecf0f1", height=60)
        user_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            user_frame,
            text=f"👤 {self.user_data['fio']}",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1"
        ).pack(pady=5)
        
        tk.Label(
            user_frame,
            text=f"🔑 Роль: {self.user_data['type']}",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#7f8c8d"
        ).pack()
        
        # Меню (кнопки)
        menu_frame = tk.Frame(self.root)
        menu_frame.pack(pady=30, fill=tk.BOTH, expand=True)
        
        # Кнопка "Заявки"
        tk.Button(
            menu_frame,
            text="📋 Заявки",
            command=self._open_requests,
            width=30,
            height=2,
            font=("Arial", 12),
            bg="#3498db",
            fg="white",
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        ).pack(pady=10)
        
        # Кнопка "Пользователи" (только для Менеджера и Оператора)
        if self.user_data['type'] in ['Менеджер', 'Оператор']:
            tk.Button(
                menu_frame,
                text="👥 Пользователи",
                command=self._open_users,
                width=30,
                height=2,
                font=("Arial", 12),
                bg="#9b59b6",
                fg="white",
                cursor="hand2",
                relief=tk.RAISED,
                bd=2
            ).pack(pady=10)
        
        # Кнопка "Отчёты"
        tk.Button(
            menu_frame,
            text="📊 Отчёты",
            command=self._open_reports,
            width=30,
            height=2,
            font=("Arial", 12),
            bg="#27ae60",
            fg="white",
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        ).pack(pady=10)
        
        # Кнопка "Выйти из системы"
        tk.Button(
            self.root,
            text="🚪 Выйти из системы",
            command=self._logout,  # ✅ Используем _logout вместо destroy
            width=30,
            height=2,
            font=("Arial", 11, "bold"),
            bg="#e74c3c",
            fg="white",
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        ).pack(pady=20)
    
    def _open_requests(self):
        """Открыть форму управления заявками."""
        self.root.withdraw()
        requests_window = tk.Toplevel(self.root)
        RequestsForm(requests_window, self.user_data, self.root)
    
    def _open_users(self):
        """Открыть форму управления пользователями."""
        self.root.withdraw()
        users_window = tk.Toplevel(self.root)
        UsersForm(users_window, self.user_data, self.root)
    
    def _open_reports(self):
        """Открыть форму отчётов."""
        self.root.withdraw()
        reports_window = tk.Toplevel(self.root)
        ReportsForm(reports_window, self.user_data, self.root)
    
    def _logout(self):
        """✅ Выйти из системы и вернуться к авторизации."""
        if messagebox.askyesno(
            "Выход из системы",
            "Вы действительно хотите выйти из системы?",
            icon='question'
        ):
            # ✅ Скрываем главное окно вместо закрытия
            self.root.withdraw()
            
            # ✅ Возвращаемся к окну авторизации
            if self.login_window:
                self.login_window.deiconify()  # Показываем окно авторизации
                self.login_window.lift()  # Поднимаем на передний план
                self.login_window.focus_force()  # Устанавливаем фокус