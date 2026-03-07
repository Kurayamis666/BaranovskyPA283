# forms/users_form.py
"""Форма управления пользователями системы."""
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection


class UsersForm:
    """Форма управления пользователями."""
    
    def __init__(self, root, user_data, parent_window):
        self.root = root
        self.user_data = user_data
        self.parent_window = parent_window
        self.root.title("Пользователи системы — АвтоТранс")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        self._create_widgets()
        self._load_users()
    
    def _create_widgets(self):
        """Создать элементы интерфейса."""
        # Заголовок
        tk.Label(self.root, text="Список пользователей", font=("Arial", 16, "bold")).pack(pady=15)
        
        # Поиск и фильтр
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(control_frame, text="🔍 Поиск:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(control_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', self._filter_users)
        
        tk.Label(control_frame, text="Роль:").pack(side=tk.LEFT, padx=15)
        self.role_var = tk.StringVar(value="Все")
        role_combo = ttk.Combobox(
            control_frame,
            textvariable=self.role_var,
            values=["Все", "Менеджер", "Автомеханик", "Оператор", "Заказчик", "Менеджер по качеству"],
            width=20,
            state="readonly"
        )
        role_combo.pack(side=tk.LEFT, padx=5)
        role_combo.bind('<<ComboboxSelected>>', self._filter_users)
        
        # Таблица пользователей
        columns = ('user_id', 'fio', 'phone', 'login', 'type')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings', height=18)
        
        headers = ['ID', 'ФИО', 'Телефон', 'Логин', 'Роль']
        widths = [50, 320, 120, 100, 150]
        
        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor='w' if col == 'fio' else 'center')
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопка "Назад"
        tk.Button(self.root, text="⬅️ Назад в меню", command=self._go_back, width=20, font=("Arial", 10)).pack(pady=10)
    
    def _load_users(self):
        """Загрузить пользователей из базы данных."""
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT user_id, fio, phone, login, type FROM users ORDER BY fio")
            
            for row in cursor.fetchall():
                values = [v if v is not None else '' for v in row]
                self.tree.insert('', tk.END, values=values)
            
            connection.close()
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Не удалось загрузить пользователей:\n{e}")
    
    def _filter_users(self, event=None):
        """Фильтрация списка пользователей по поиску и роли."""
        search_text = self.search_var.get().strip().lower()
        role_filter = self.role_var.get()
        
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            connection = get_connection()
            cursor = connection.cursor()
            
            query = "SELECT user_id, fio, phone, login, type FROM users WHERE 1=1"
            params = []
            
            # Поиск по ФИО, логину или телефону
            if search_text:
                query += " AND (LOWER(fio) LIKE ? OR LOWER(login) LIKE ? OR phone LIKE ?)"
                params.extend([f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'])
            
            # Фильтр по роли
            if role_filter != "Все":
                query += " AND type = ?"
                params.append(role_filter)
            
            query += " ORDER BY fio"
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                values = [v if v is not None else '' for v in row]
                self.tree.insert('', tk.END, values=values)
            
            connection.close()
        except Exception as e:
            messagebox.showerror("Ошибка фильтрации", f"Не удалось отфильтровать:\n{e}")
    
    def _go_back(self):
        """Вернуться в главное меню."""
        self.root.destroy()
        if self.parent_window:
            self.parent_window.deiconify()