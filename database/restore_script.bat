@echo off
REM ============================================================================
REM СКРИПТ ВОССТАНОВЛЕНИЯ БАЗЫ ДАННЫХ
REM ============================================================================

SET PGUSER=auto_app
SET PGPASSWORD=AutoApp2024!
SET PGHOST=localhost
SET PGPORT=5432

SET BACKUP_FILE=%1

IF "%BACKUP_FILE%"=="" (
    echo Использование: restore.bat путь_к_файлу.backup
    PAUSE
    EXIT /B
)

REM Восстановление
pg_restore -h %PGHOST% -U %PGUSER% -d auto_service -v "%BACKUP_FILE%"

IF %ERRORLEVEL% EQU 0 (
    echo [OK] База данных восстановлена!
) ELSE (
    echo [ERROR] Ошибка восстановления!
)

PAUSE