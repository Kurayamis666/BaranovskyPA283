-- ============================================================================
-- ПРОВЕРКА ЦЕЛОСТНОСТИ ДАННЫХ
-- ============================================================================

-- 1. Проверка количества записей
SELECT 
    'users' AS table_name, COUNT(*) AS records FROM users
UNION ALL SELECT 'requests', COUNT(*) FROM requests
UNION ALL SELECT 'comments', COUNT(*) FROM comments
UNION ALL SELECT 'quality_surveys', COUNT(*) FROM quality_surveys;

-- 2. Проверка ссылочной целостности (заявки без клиента)
SELECT COUNT(*) AS orphan_requests 
FROM requests 
WHERE client_id NOT IN (SELECT user_id FROM users);

-- 3. Проверка дубликатов логинов
SELECT login, COUNT(*) 
FROM users 
GROUP BY login 
HAVING COUNT(*) > 1;

-- 4. Проверка корректности статусов
SELECT DISTINCT request_status FROM requests;

-- 5. Проверка дат (завершение раньше начала)
SELECT COUNT(*) AS invalid_dates 
FROM requests 
WHERE completion_date IS NOT NULL 
  AND completion_date < start_date;

-- 6. Проверка внешних ключей comments
SELECT COUNT(*) AS orphan_comments 
FROM comments 
WHERE request_id NOT IN (SELECT request_id FROM requests);