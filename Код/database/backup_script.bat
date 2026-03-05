@echo off
REM ============================================================================
REM СКРИПТ РЕЗЕРВНОГО КОПИРОВАНИЯ БАЗЫ ДАННЫХ
REM ============================================================================

SET PGUSER=auto_app
SET PGPASSWORD=AutoApp2024!
SET PGHOST=localhost
SET PGPORT=5432
SET PGDATABASE=auto_service

SET BACKUP_DIR=C:\Backups\auto_service
SET DATE=%DATE:~-4,4%%DATE:~-7,2%%DATE:~-10,2%_%TIME:~0,2%%TIME:~3,2%
SET BACKUP_FILE=%BACKUP_DIR%\auto_service_%DATE%.sql

REM Создание директории
IF NOT EXIST "%BACKUP_DIR%" MKDIR "%BACKUP_DIR%"

REM Резервное копирование
pg_dump -h %PGHOST% -U %PGUSER% -d %PGDATABASE% -F c -b -v -f "%BACKUP_FILE%"

REM Проверка результата
IF %ERRORLEVEL% EQU 0 (
    echo [OK] Резервная копия создана: %BACKUP_FILE%
) ELSE (
    echo [ERROR] Ошибка создания резервной копии!
)

PAUSE