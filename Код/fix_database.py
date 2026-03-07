# fix_database.py
"""Добавление недостающих колонок в базу данных."""

from database import get_connection

def fix_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    print("🔧 Исправление структуры БД...\n")
    
    # 1. Добавляем comment_text в comments
    try:
        cursor.execute("ALTER TABLE comments ADD COLUMN comment_text TEXT")
        print("✅ Добавлена колонка comment_text в таблицу comments")
    except Exception as e:
        print(f"⚠️  comment_text: {e}")
    
    # 2. Добавляем client_id в quality_surveys
    try:
        cursor.execute("ALTER TABLE quality_surveys ADD COLUMN client_id INTEGER")
        print("✅ Добавлена колонка client_id в таблицу quality_surveys")
    except Exception as e:
        print(f"⚠️  client_id: {e}")
    
    # 3. Добавляем survey_date в quality_surveys
    try:
        cursor.execute("ALTER TABLE quality_surveys ADD COLUMN survey_date TEXT")
        print("✅ Добавлена колонка survey_date в таблицу quality_surveys")
    except Exception as e:
        print(f"⚠️  survey_date: {e}")
    
    conn.commit()
    
    # Обновляем существующие данные
    try:
        # Устанавливаем survey_date = текущая дата для существующих записей
        cursor.execute("UPDATE quality_surveys SET survey_date = DATE('now') WHERE survey_date IS NULL")
        print("✅ Обновлены значения survey_date")
    except:
        pass
    
    conn.close()
    print("\n✅ Исправление завершено!")

if __name__ == "__main__":
    fix_database()