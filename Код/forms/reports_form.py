# forms/reports_form.py
"""Форма отчётов и статистики."""
import tkinter as tk
from tkinter import ttk
from database import get_connection
from utils.statistics import get_full_statistics


class ReportsForm:
    """Форма отображения статистики."""
    
    def __init__(self, root, user_data, parent_window):
        self.root = root
        self.user_data = user_data
        self.parent_window = parent_window
        self.root.title("Отчёты и статистика — АвтоТранс")
        self.root.geometry("850x700")
        self._create_widgets()
        self._load_statistics()
    
    def _create_widgets(self):
        """Создать элементы интерфейса."""
        # Заголовок
        tk.Label(
            self.root,
            text="📊 Статистика работы автосервиса",
            font=("Arial", 16, "bold")
        ).pack(pady=15)
        
        # Блок основных показателей
        stats_frame = tk.LabelFrame(self.root, text="Основные показатели", padx=15, pady=10)
        stats_frame.pack(fill=tk.X, padx=20, pady=5)
        
        self.stats = {}
        stats_items = [
            ("total", "📋 Всего заявок:"),
            ("completed", "✅ Завершено:"),
            ("in_progress", "🔧 В работе:"),
            ("new", "🆕 Новые:"),
            ("avg_time", "⏱️ Среднее время ремонта:"),
            ("top_issue", "🔍 Частая неисправность:"),
        ]
        
        for key, label in stats_items:
            frame = tk.Frame(stats_frame)
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, text=label, font=("Arial", 11), width=35, anchor='e').pack(side=tk.LEFT)
            self.stats[key] = tk.Label(frame, text="—", font=("Arial", 11, "bold"), anchor='w')
            self.stats[key].pack(side=tk.LEFT, padx=10)
        
        # Таблица по механикам
        tk.Label(self.root, text="👨‍🔧 Статистика по автомеханикам", font=("Arial", 12, "bold")).pack(pady=15)
        
        columns = ('master_fio', 'completed', 'avg_time')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings', height=10)
        
        self.tree.heading('master_fio', text='Механик')
        self.tree.heading('completed', text='Завершено заявок')
        self.tree.heading('avg_time', text='Среднее время (дн.)')
        
        self.tree.column('master_fio', width=320)
        self.tree.column('completed', width=150, anchor='center')
        self.tree.column('avg_time', width=150, anchor='center')
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Кнопка "Назад"
        tk.Button(
            self.root,
            text="⬅️ Назад в меню",
            command=self._go_back,
            width=20,
            font=("Arial", 10)
        ).pack(pady=15)
    
    def _load_statistics(self):
        """Загрузить и отобразить статистику."""
        stats = get_full_statistics()
        
        # Обновление основных показателей
        self.stats['total'].config(text=str(stats['total_requests']))
        self.stats['completed'].config(text=str(stats['completed_requests']))
        self.stats['in_progress'].config(text=str(stats['in_progress']))
        self.stats['new'].config(text=str(stats['new_requests']))
        self.stats['avg_time'].config(text=f"{stats['average_repair_time']} дн.")
        
        top_issue = stats['top_issues'][0][0] if stats['top_issues'] else "—"
        if len(top_issue) > 30:
            top_issue = top_issue[:27] + "..."
        self.stats['top_issue'].config(text=top_issue)
        
        # Заполнение таблицы по механикам
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for master in stats['master_statistics']:
            self.tree.insert('', tk.END, values=(
                master['fio'],
                master['completed'],
                f"{master['avg_time']} дн."
            ))
    
    def _go_back(self):
        """Вернуться в главное меню."""
        self.root.destroy()
        if self.parent_window:
            self.parent_window.deiconify()