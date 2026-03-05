# utils/notifications.py
"""Модуль уведомлений пользователей."""
import tkinter as tk
from tkinter import messagebox
from database import get_connection


def show_notification(title, message, level='info'):
    """Показать уведомление пользователю."""
    if level == 'info':
        messagebox.showinfo(title, message)
    elif level == 'warning':
        messagebox.showwarning(title, message)
    elif level == 'error':
        messagebox.showerror(title, message)
    elif level == 'question':
        return messagebox.askyesno(title, message)


def notify_status_change(request_id, old_status, new_status, user_fio):
    """Уведомить о смене статуса заявки."""
    message = (
        f"Заявка №{request_id}\n\n"
        f"Статус изменён: {old_status} → {new_status}\n"
        f"Пользователь: {user_fio}"
    )
    show_notification("Смена статуса заявки", message, 'info')
    _log_status_change(request_id, old_status, new_status, user_fio)


def _log_status_change(request_id, old_status, new_status, user_fio):
    """Записать изменение статуса в лог."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT user_id FROM users WHERE fio = ?", (user_fio,))
    result = cursor.fetchone()
    master_id = result[0] if result else None
    
    cursor.execute('''
        INSERT INTO comments (message, master_id, request_id)
        VALUES (?, ?, ?)
    ''', (f"Статус изменён: {old_status} → {new_status}", master_id, request_id))
    connection.commit()
    connection.close()


def confirm_delete_request(request_id):
    """Запросить подтверждение удаления заявки."""
    return show_notification(
        "Подтверждение удаления",
        f"Вы действительно хотите удалить заявку №{request_id}?\n\nЭто действие нельзя отменить!",
        'question'
    )