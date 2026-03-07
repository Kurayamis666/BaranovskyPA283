# forms/requests_form.py
"""Форма управления заявками на ремонт автомобилей."""
import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection
from utils.qr_generator import generate_qr_code
from utils.notifications import notify_status_change


class RequestsForm:
    """Форма управления заявками на ремонт."""
    
    def __init__(self, root, user_data, parent_window):
        self.root = root
        self.user_data = user_data
        self.parent_window = parent_window
        self.root.title("Управление заявками — АвтоТранс")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        self._create_widgets()
        self._load_requests()
    
    def _create_widgets(self):
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(control_frame, text="🔍 Поиск:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(control_frame, width=25, font=("Arial", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<Return>', lambda e: self._search_requests())
        tk.Button(control_frame, text="Найти", command=self._search_requests, width=8, cursor="hand2").pack(side=tk.LEFT, padx=5)
        
        tk.Label(control_frame, text="Статус:", font=("Arial", 10)).pack(side=tk.LEFT, padx=15)
        self.status_var = tk.StringVar(value="Все")
        status_combo = ttk.Combobox(control_frame, textvariable=self.status_var,
            values=["Все", "Новая заявка", "В процессе ремонта", "Готова к выдаче", "Завершена", "Ожидание запчастей"],
            width=20, state="readonly", font=("Arial", 10))
        status_combo.pack(side=tk.LEFT, padx=5)
        status_combo.bind('<<ComboboxSelected>>', self._filter_by_status)
        
        if self.user_data['type'] in ['Менеджер', 'Оператор', 'Менеджер по качеству']:
            tk.Button(control_frame, text="➕ Новая заявка", command=self._add_request,
                bg="#27ae60", fg="white", width=15, font=("Arial", 10, "bold"), cursor="hand2").pack(side=tk.RIGHT, padx=5)
        
        columns = ('request_id', 'start_date', 'car_type', 'car_model', 'problem_description', 'request_status', 'master_fio', 'client_fio', 'client_phone')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings', height=20)
        headers = ['№', 'Дата', 'Тип авто', 'Модель', 'Проблема', 'Статус', 'Мастер', 'Клиент', 'Телефон']
        widths = [50, 100, 80, 150, 200, 130, 150, 180, 120]
        for col, header, width in zip(columns, headers, widths):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=width, anchor='w' if col == 'problem_description' else 'center')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)
        self.edit_btn = tk.Button(btn_frame, text="✏️ Редактировать", command=self._edit_request, width=18, state=tk.DISABLED, cursor="hand2")
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        self.qr_btn = tk.Button(btn_frame, text="🔗 QR-код", command=self._generate_qr, width=18, state=tk.DISABLED, cursor="hand2")
        self.qr_btn.pack(side=tk.LEFT, padx=5)
        if self.user_data['type'] in ['Менеджер', 'Оператор', 'Менеджер по качеству']:
            self.delete_btn = tk.Button(btn_frame, text="🗑️ Удалить", command=self._delete_request, width=18, bg="#e74c3c", fg="white", state=tk.DISABLED, cursor="hand2")
            self.delete_btn.pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="⬅️ Назад", command=self._go_back, width=18, cursor="hand2").pack(side=tk.RIGHT, padx=5)
    
    def _load_requests(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute('''
                SELECT r.request_id, r.start_date, r.car_type, r.car_model,
                       r.problem_description, r.request_status,
                       m.fio as master_fio, c.fio as client_fio, c.phone as client_phone
                FROM requests r
                LEFT JOIN users m ON r.master_id = m.user_id
                LEFT JOIN users c ON r.client_id = c.user_id
                ORDER BY r.request_id DESC
            ''')
            for row in cursor.fetchall():
                values = [v if v is not None else '' for v in row]
                self.tree.insert('', tk.END, values=values)
            connection.close()
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Не удалось загрузить заявки:\n{e}")
    
    def _search_requests(self):
        search_text = self.search_entry.get().strip().lower()
        if not search_text:
            self._load_requests()
            return
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            connection = get_connection()
            cursor = connection.cursor()
            cursor.execute('''
                SELECT r.request_id, r.start_date, r.car_type, r.car_model,
                       r.problem_description, r.request_status,
                       m.fio as master_fio, c.fio as client_fio, c.phone as client_phone
                FROM requests r
                LEFT JOIN users m ON r.master_id = m.user_id
                LEFT JOIN users c ON r.client_id = c.user_id
                WHERE LOWER(r.car_model) LIKE ? OR LOWER(r.problem_description) LIKE ? OR LOWER(c.fio) LIKE ? OR c.phone LIKE ?
                ORDER BY r.request_id DESC
            ''', (f'%{search_text}%', f'%{search_text}%', f'%{search_text}%', f'%{search_text}%'))
            for row in cursor.fetchall():
                values = [v if v is not None else '' for v in row]
                self.tree.insert('', tk.END, values=values)
            connection.close()
        except Exception as e:
            messagebox.showerror("Ошибка поиска", f"Не удалось выполнить поиск:\n{e}")
    
    def _filter_by_status(self, event=None):
        status = self.status_var.get()
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            connection = get_connection()
            cursor = connection.cursor()
            if status == "Все":
                cursor.execute('''
                    SELECT r.request_id, r.start_date, r.car_type, r.car_model,
                           r.problem_description, r.request_status,
                           m.fio as master_fio, c.fio as client_fio, c.phone as client_phone
                    FROM requests r
                    LEFT JOIN users m ON r.master_id = m.user_id
                    LEFT JOIN users c ON r.client_id = c.user_id
                    ORDER BY r.request_id DESC
                ''')
            else:
                cursor.execute('''
                    SELECT r.request_id, r.start_date, r.car_type, r.car_model,
                           r.problem_description, r.request_status,
                           m.fio as master_fio, c.fio as client_fio, c.phone as client_phone
                    FROM requests r
                    LEFT JOIN users m ON r.master_id = m.user_id
                    LEFT JOIN users c ON r.client_id = c.user_id
                    WHERE r.request_status = ?
                    ORDER BY r.request_id DESC
                ''', (status,))
            for row in cursor.fetchall():
                values = [v if v is not None else '' for v in row]
                self.tree.insert('', tk.END, values=values)
            connection.close()
        except Exception as e:
            messagebox.showerror("Ошибка фильтрации", f"Не удалось отфильтровать заявки:\n{e}")
    
    def _on_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.edit_btn.config(state=tk.NORMAL)
            self.qr_btn.config(state=tk.NORMAL)
            if self.user_data['type'] in ['Менеджер', 'Оператор', 'Менеджер по качеству']:
                self.delete_btn.config(state=tk.NORMAL)
        else:
            self.edit_btn.config(state=tk.DISABLED)
            self.qr_btn.config(state=tk.DISABLED)
            if self.user_data['type'] in ['Менеджер', 'Оператор', 'Менеджер по качеству']:
                self.delete_btn.config(state=tk.DISABLED)
    
    def _add_request(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("➕ Новая заявка — АвтоТранс")
        add_window.geometry("550x450")
        add_window.resizable(True, True)
        add_window.transient(self.root)
        add_window.grab_set()
        tk.Label(add_window, text="Создание новой заявки", font=("Arial", 14, "bold")).pack(pady=15)
        form_frame = tk.Frame(add_window)
        form_frame.pack(pady=10, padx=20, fill=tk.X)
        fields = {}
        tk.Label(form_frame, text="Тип авто *:", font=("Arial", 10)).grid(row=0, column=0, sticky='e', padx=10, pady=8)
        fields['car_type'] = ttk.Combobox(form_frame, values=["Легковая", "Грузовая"], width=30, state="readonly")
        fields['car_type'].grid(row=0, column=1, padx=10, pady=8)
        fields['car_type'].current(0)
        tk.Label(form_frame, text="Модель авто *:", font=("Arial", 10)).grid(row=1, column=0, sticky='e', padx=10, pady=8)
        fields['car_model'] = tk.Entry(form_frame, width=32, font=("Arial", 10))
        fields['car_model'].grid(row=1, column=1, padx=10, pady=8)
        tk.Label(form_frame, text="Описание проблемы *:", font=("Arial", 10)).grid(row=2, column=0, sticky='ne', padx=10, pady=8)
        fields['problem'] = tk.Text(form_frame, width=30, height=4, font=("Arial", 10))
        fields['problem'].grid(row=2, column=1, padx=10, pady=8)
        tk.Label(form_frame, text="Клиент *:", font=("Arial", 10)).grid(row=3, column=0, sticky='e', padx=10, pady=8)
        fields['client'] = ttk.Combobox(form_frame, width=30, state="readonly", font=("Arial", 10))
        fields['client'].grid(row=3, column=1, padx=10, pady=8)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, fio FROM users WHERE type = 'Заказчик' ORDER BY fio")
            clients = cursor.fetchall()
            conn.close()
            client_values = [f"{c[0]} - {c[1]}" for c in clients]
            fields['client']['values'] = client_values
            if client_values:
                fields['client'].current(0)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить список клиентов:\n{e}")
            add_window.destroy()
            return
        tk.Label(add_window, text="* — обязательные поля", font=("Arial", 9), fg="#666").pack(pady=5)
        btn_frame = tk.Frame(add_window)
        btn_frame.pack(pady=20)
        def save_request():
            car_type = fields['car_type'].get()
            car_model = fields['car_model'].get().strip()
            problem = fields['problem'].get("1.0", tk.END).strip()
            client_selection = fields['client'].get()
            errors = []
            if not car_model: errors.append("Модель автомобиля")
            if not problem: errors.append("Описание проблемы")
            if not client_selection: errors.append("Клиент")
            if errors:
                messagebox.showwarning("Ошибка ввода", f"Заполните обязательные поля:\n• " + "\n• ".join(errors))
                return
            client_id = int(client_selection.split(' - ')[0])
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT COALESCE(MAX(request_id), 0) + 1 FROM requests")
                new_id = cursor.fetchone()[0]
                cursor.execute('''
                    INSERT INTO requests (request_id, start_date, car_type, car_model, problem_description, request_status, client_id)
                    VALUES (?, DATE('now'), ?, ?, ?, 'Новая заявка', ?)
                ''', (new_id, car_type, car_model, problem, client_id))
                conn.commit()
                conn.close()
                add_window.destroy()
                self._load_requests()
                messagebox.showinfo("Успех", f"Заявка №{new_id} успешно создана!")
            except Exception as e:
                messagebox.showerror("Ошибка БД", f"Не удалось сохранить заявку:\n{e}")
        tk.Button(btn_frame, text="💾 Сохранить", command=save_request, width=15, bg="#27ae60", fg="white", font=("Arial", 10, "bold"), cursor="hand2").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="❌ Отмена", command=add_window.destroy, width=15, cursor="hand2").pack(side=tk.LEFT, padx=10)
        fields['car_model'].focus()
        add_window.bind('<Return>', lambda e: save_request())
    
    def _edit_request(self):
        """Редактировать выбранную заявку."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заявку для редактирования.")
            return
        
        item = self.tree.item(selected[0])
        request_id = int(item['values'][0])
        current_status = str(item['values'][5]).strip()
        current_master = item['values'][6]
        
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"✏️ Редактирование заявки №{request_id}")
        edit_window.geometry("500x400")
        edit_window.resizable(True, True)
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        tk.Label(edit_window, text=f"Заявка №{request_id}", font=("Arial", 14, "bold")).pack(pady=15)
        
        form_frame = tk.Frame(edit_window)
        form_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # ===== СТАТУС =====
        tk.Label(form_frame, text="Статус *:", font=("Arial", 10)).grid(row=0, column=0, sticky='e', padx=10, pady=8)
        status_values = ["Новая заявка", "В процессе ремонта", "Готова к выдаче", "Завершена", "Ожидание запчастей"]
        self.edit_status_combo = ttk.Combobox(form_frame, values=status_values, width=30, state="readonly", font=("Arial", 10))
        self.edit_status_combo.grid(row=0, column=1, padx=10, pady=8)
        try:
            status_index = status_values.index(current_status)
            self.edit_status_combo.current(status_index)
        except ValueError:
            self.edit_status_combo.current(0)
        
        # ===== МАСТЕР =====
        tk.Label(form_frame, text="Мастер:", font=("Arial", 10)).grid(row=1, column=0, sticky='e', padx=10, pady=8)
        self.edit_master_combo = ttk.Combobox(form_frame, width=30, font=("Arial", 10))
        self.edit_master_combo.grid(row=1, column=1, padx=10, pady=8)
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, fio FROM users WHERE type = 'Автомеханик' ORDER BY fio")
            mechanics = cursor.fetchall()
            conn.close()
            mechanic_values = ["Не назначен"] + [f"{m[0]} - {m[1]}" for m in mechanics]
            self.edit_master_combo['values'] = mechanic_values
            if current_master:
                for i, val in enumerate(mechanic_values):
                    if current_master in val:
                        self.edit_master_combo.current(i)
                        break
            else:
                self.edit_master_combo.current(0)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить список механиков:\n{e}")
        
        # ===== КНОПКИ =====
        btn_frame = tk.Frame(edit_window)
        btn_frame.pack(pady=20)
        
        def save_changes():
            new_status = self.edit_status_combo.get().strip()
            master_selection = self.edit_master_combo.get()
            
            if master_selection == "Не назначен":
                new_master_id = None
            else:
                try:
                    new_master_id = int(master_selection.split(' - ')[0])
                except:
                    new_master_id = None
            
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute('UPDATE requests SET request_status = ?, master_id = ? WHERE request_id = ?',
                              (new_status, new_master_id, request_id))
                conn.commit()
                conn.close()
                
                edit_window.destroy()
                self._load_requests()
                messagebox.showinfo("Успех", f"Заявка №{request_id} обновлена!\nНовый статус: {new_status}")
            except Exception as e:
                messagebox.showerror("Ошибка БД", f"Не удалось сохранить изменения:\n{e}")
        
        tk.Button(btn_frame, text="💾 Сохранить", command=save_changes, width=15, bg="#27ae60", fg="white", font=("Arial", 10, "bold"), cursor="hand2").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="❌ Отмена", command=edit_window.destroy, width=15, cursor="hand2").pack(side=tk.LEFT, padx=10)
    
    def _generate_qr(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заявку для генерации QR-кода.")
            return
        request_id = self.tree.item(selected[0])['values'][0]
        status = self.tree.item(selected[0])['values'][5]
        if status not in ['Готова к выдаче', 'Завершена']:
            messagebox.showwarning("Внимание", "QR-код доступен только для заявок со статусом «Готова к выдаче» или «Завершена»")
            return
        try:
            qr_path = generate_qr_code(request_id)
            messagebox.showinfo("QR-код сгенерирован", f"Файл сохранён:\n{qr_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сгенерировать QR-код:\n{e}")
    
    def _delete_request(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заявку для удаления.")
            return
        request_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Подтверждение удаления", f"Вы действительно хотите удалить заявку №{request_id}?"):
            try:
                connection = get_connection()
                cursor = connection.cursor()
                cursor.execute("DELETE FROM requests WHERE request_id = ?", (request_id,))
                connection.commit()
                connection.close()
                self._load_requests()
                messagebox.showinfo("Успех", "Заявка успешно удалена.")
            except Exception as e:
                messagebox.showerror("Ошибка БД", f"Не удалось удалить заявку:\n{e}")
    
    def _go_back(self):
        self.root.destroy()
        self.parent_window.deiconify()