-- ============================================================================
-- ИМПОРТ ДАННЫХ ИЗ CSV-ФАЙЛОВ
-- ============================================================================

-- Временные таблицы для импорта
CREATE TEMP TABLE temp_users (
    user_id INTEGER,
    fio VARCHAR(200),
    phone VARCHAR(20),
    login VARCHAR(50),
    password VARCHAR(100),
    type VARCHAR(50)
);

CREATE TEMP TABLE temp_requests (
    request_id INTEGER,
    start_date DATE,
    car_type VARCHAR(50),
    car_model VARCHAR(100),
    problem_description TEXT,
    request_status VARCHAR(50),
    completion_date DATE,
    repair_parts TEXT,
    master_id INTEGER,
    client_id INTEGER
);

CREATE TEMP TABLE temp_comments (
    comment_id INTEGER,
    message TEXT,
    master_id INTEGER,
    request_id INTEGER
);

-- Импорт пользователей
COPY temp_users (user_id, fio, phone, login, password, type)
FROM 'C:/path/to/inputDataUsers.csv'
DELIMITER ';'
CSV HEADER
ENCODING 'UTF8';

-- Перенос данных в основную таблицу
INSERT INTO users (user_id, fio, phone, login, password, type)
SELECT user_id, fio, phone, login, password, type
FROM temp_users
ON CONFLICT (user_id) DO UPDATE SET
    fio = EXCLUDED.fio,
    phone = EXCLUDED.phone,
    type = EXCLUDED.type;

-- Сброс последовательности
SELECT setval('users_user_id_seq', (SELECT MAX(user_id) FROM users));

-- Импорт заявок
COPY temp_requests (request_id, start_date, car_type, car_model, problem_description, 
                   request_status, completion_date, repair_parts, master_id, client_id)
FROM 'C:/path/to/inputDataRequests.csv'
DELIMITER ';'
CSV HEADER
ENCODING 'UTF8'
NULL 'null';

-- Перенос данных в основную таблицу
INSERT INTO requests (request_id, start_date, car_type, car_model, problem_description,
                     request_status, completion_date, repair_parts, master_id, client_id)
SELECT request_id, start_date, car_type, car_model, problem_description,
       request_status, NULLIF(completion_date, 'null'), repair_parts, 
       NULLIF(master_id, ''), NULLIF(client_id, '')
FROM temp_requests
ON CONFLICT (request_id) DO UPDATE SET
    request_status = EXCLUDED.request_status,
    completion_date = EXCLUDED.completion_date,
    master_id = EXCLUDED.master_id;

-- Сброс последовательности
SELECT setval('requests_request_id_seq', (SELECT MAX(request_id) FROM requests));

-- Импорт комментариев
COPY temp_comments (comment_id, message, master_id, request_id)
FROM 'C:/path/to/inputDataComments.csv'
DELIMITER ';'
CSV HEADER
ENCODING 'UTF8';

-- Перенос данных в основную таблицу
INSERT INTO comments (comment_id, message, master_id, request_id)
SELECT comment_id, message, master_id, request_id
FROM temp_comments
ON CONFLICT (comment_id) DO UPDATE SET
    message = EXCLUDED.message;

-- Сброс последовательности
SELECT setval('comments_comment_id_seq', (SELECT MAX(comment_id) FROM comments));

-- Очистка временных таблиц
DROP TABLE temp_users;
DROP TABLE temp_requests;
DROP TABLE temp_comments;

-- ============================================================================
-- ПРОВЕРКА ИМПОРТА
-- ============================================================================

SELECT 'users' AS table_name, COUNT(*) AS record_count FROM users
UNION ALL
SELECT 'requests', COUNT(*) FROM requests
UNION ALL
SELECT 'comments', COUNT(*) FROM comments;