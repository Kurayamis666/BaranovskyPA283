-- ============================================================================
-- ОТЧЁТЫ И ЗАПРОСЫ ДЛЯ АВТОСЕРВИСА
-- ============================================================================

-- 1. Список всех заявок с полной информацией
SELECT * FROM v_requests_full ORDER BY request_id DESC;

-- 2. Заявки по статусам
SELECT request_status, COUNT(*) AS count
FROM requests
GROUP BY request_status
ORDER BY count DESC;

-- 3. Новые заявки (без назначенного механика)
SELECT r.request_id, r.start_date, r.car_model, r.problem_description, c.fio AS client
FROM requests r
JOIN users c ON r.client_id = c.user_id
WHERE r.master_id IS NULL 
  AND r.request_status = 'Новая заявка'
ORDER BY r.start_date;

-- 4. Статистика по механикам
SELECT * FROM v_mechanic_statistics ORDER BY completed_requests DESC;

-- 5. Среднее время ремонта
SELECT fn_get_average_repair_time() AS avg_repair_days;

-- 6. Топ-5 частых неисправностей
SELECT problem_description, COUNT(*) AS frequency
FROM requests
WHERE problem_description IS NOT NULL
GROUP BY problem_description
ORDER BY frequency DESC
LIMIT 5;

-- 7. Заявки с просрочкой (более 30 дней в работе)
SELECT r.request_id, r.car_model, r.start_date, 
       CURRENT_DATE - r.start_date AS days_in_progress,
       m.fio AS mechanic
FROM requests r
LEFT JOIN users m ON r.master_id = m.user_id
WHERE r.request_status IN ('В процессе ремонта', 'Ожидание запчастей')
  AND CURRENT_DATE - r.start_date > 30
ORDER BY days_in_progress DESC;

-- 8. Комментарии по заявке
SELECT c.comment_id, c.message, u.fio AS author, c.created_at
FROM comments c
LEFT JOIN users u ON c.master_id = u.user_id
WHERE c.request_id = 1
ORDER BY c.created_at;

-- 9. Опросы качества (рейтинг)
SELECT 
    qs.survey_id,
    r.request_id,
    qs.rating,
    qs.feedback,
    c.fio AS client_name
FROM quality_surveys qs
JOIN requests r ON qs.request_id = r.request_id
JOIN users c ON r.client_id = c.user_id
WHERE qs.rating IS NOT NULL
ORDER BY qs.created_at DESC;

-- 10. Средний рейтинг качества
SELECT 
    ROUND(AVG(rating), 2) AS avg_rating,
    COUNT(*) AS total_surveys,
    COUNT(CASE WHEN rating >= 4 THEN 1 END) AS positive_reviews
FROM quality_surveys
WHERE rating IS NOT NULL;

-- 11. Журнал изменений заявки
SELECT 
    rl.action_date,
    u.fio AS user_name,
    rl.action_type,
    rl.description,
    rl.old_value,
    rl.new_value
FROM request_logs rl
LEFT JOIN users u ON rl.user_id = u.user_id
WHERE rl.request_id = 1
ORDER BY rl.action_date DESC;

-- 12. Нагрузка по механикам за месяц
SELECT 
    m.fio AS mechanic,
    COUNT(r.request_id) AS requests_count,
    COUNT(CASE WHEN r.request_status = 'Завершена' THEN 1 END) AS completed
FROM users m
LEFT JOIN requests r ON m.user_id = r.master_id
    AND r.start_date >= DATE_TRUNC('month', CURRENT_DATE)
WHERE m.type = 'Автомеханик'
GROUP BY m.user_id, m.fio
ORDER BY requests_count DESC;