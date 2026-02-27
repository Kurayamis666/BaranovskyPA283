# forms/main_form.py
"""Главное окно приложения после авторизации."""
import tkinter as tk
from tkinter import messagebox
from .requests_form import RequestsForm
from .users_form import UsersForm
from .reports_form import ReportsForm


class MainForm:
    """Главное окно приложения."""
    
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        self.root.title(f"Главное меню — {user_data['fio']}")
        self.root.geometry("500x450")
        self.root.resizable(False, False)
        self._create_widgets()
    
    def _create_widgets(self):
        """Создать элементы главного меню."""
        # Шапка
        header = tk.Frame(self.root, bg="#2c3e50", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🔧 Автосервис «АвтоТранс»",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=20)
        
        # Информация о пользователе
        user_info = tk.Label(
            self.root,
            text=f"👤 {self.user_data['fio']}\n🔑 Роль: {self.user_data['type']}",
            font=("Arial", 11),
            justify=tk.LEFT
        )
        user_info.pack(pady=15)
        
        # Меню
        menu_frame = tk.Frame(self.root)
        menu_frame.pack(pady=20)
        
        buttons = [
            ("📋 Заявки", self._open_requests, 0),
            ("👥 Пользователи", self._open_users, 1),
            ("📊 Отчёты", self._open_reports, 2),
        ]
        
        for text, command, row in buttons:
            tk.Button(
                menu_frame,
                text=text,
                command=command,
                width=30,
                height=2,
                font=("Arial", 11),
                cursor="hand2"
            ).grid(row=row, column=0, pady=8)
        
        # Кнопка выхода
        tk.Button(
            self.root,
            text="🚪 Выйти из системы",
            command=self._exit_application,
            width=30,
            height=2,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2"
        ).pack(pady=25)
    
    def _open_requests(self):
        """Открыть форму управления заявками."""
        self.root.withdraw()
        requests_window = tk.Toplevel(self.root)
        RequestsForm(requests_window, self.user_data, self.root)
    
    def _open_users(self):
        """Открыть форму управления пользователями."""
        if self.user_data['type'] not in ['Менеджер', 'Оператор']:
            messagebox.showwarning(
                "Доступ запрещён",
                "Только Менеджер и Оператор могут управлять пользователями."
            )
            return
        self.root.withdraw()
        users_window = tk.Toplevel(self.root)
        UsersForm(users_window, self.user_data, self.root)
    
    def _open_reports(self):
        """Открыть форму отчётов."""
        self.root.withdraw()
        reports_window = tk.Toplevel(self.root)
        ReportsForm(reports_window, self.user_data, self.root)
    
    def _exit_application(self):
        """Выйти из приложения."""
        if messagebox.askyesno("Выход", "Вы действительно хотите выйти из системы?"):
            self.root.destroy()