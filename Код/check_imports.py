import sys
import os
from pathlib import Path

print("🔍 Диагностика импортов")
print(f"Рабочая директория: {os.getcwd()}")
print(f"Python путь: {sys.path}\n")

forms_path = Path(__file__).parent / "forms"
print(f"📁 Папка forms существует: {forms_path.exists()}")

if forms_path.exists():
    files = list(forms_path.glob("*.py"))
    print(f"📄 Файлы в forms/: {[f.name for f in files]}")
    
    required = ["__init__.py", "users_form.py", "reports_form.py", "main_form.py"]
    for req in required:
        status = "✅" if (forms_path / req).exists() else "❌"
        print(f"  {status} {req}")