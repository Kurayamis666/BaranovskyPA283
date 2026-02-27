-- ============================================================================
-- БАЗА ДАННЫХ: auto_service
-- НАЗНАЧЕНИЕ: Учёт заявок на ремонт автомобилей
-- ВЕРСИЯ: 1.0
-- ДАТА: 2024
-- ============================================================================

-- Удаление существующей БД (если есть)
DROP DATABASE IF EXISTS auto_service;
DROP USER IF EXISTS auto_admin;
DROP USER IF EXISTS auto_manager;
DROP USER IF EXISTS auto_mechanic;
DROP USER IF EXISTS auto_operator;

-- Создание базы данных
CREATE DATABASE auto_service
    WITH ENCODING = 'UTF8'
    LC_COLLATE = 'ru_RU.UTF-8'
    LC_CTYPE = 'ru_RU.UTF-8'
    TEMPLATE = template0;

-- Подключение к БД
\c auto_service;

-- ============================================================================
-- ТАБЛИЦА: users (Пользователи системы)
-- ============================================================================
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    fio VARCHAR(200) NOT NULL,
    phone VARCHAR(20),
    login VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN (
        'Менеджер', 
        'Автомеханик', 
        'Оператор', 
        'Заказчик', 
        'Менеджер по качеству'
    )),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Индексы для users
CREATE INDEX idx_users_login ON users(login);
CREATE INDEX idx_users_type ON users(type);
CREATE INDEX idx_users_fio ON users(fio);

-- ============================================================================
-- ТАБЛИЦА: requests (Заявки на ремонт)
-- ============================================================================
CREATE TABLE requests (
    request_id SERIAL PRIMARY KEY,
    start_date DATE NOT NULL,
    car_type VARCHAR(50),
    car_model VARCHAR(100),
    problem_description TEXT,
    request_status VARCHAR(50) NOT NULL CHECK (request_status IN (
        'Новая заявка',
        'В процессе ремонта',
        'Готова к выдаче',
        'Завершена',
        'Ожидание запчастей'
    )),
    completion_date DATE,
    repair_parts TEXT,
    master_id INTEGER,
    client_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Внешние ключи
    CONSTRAINT fk_requests_master 
        FOREIGN KEY (master_id) REFERENCES users(user_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_requests_client 
        FOREIGN KEY (client_id) REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    -- Проверка: дата завершения >= даты начала
    CONSTRAINT chk_dates CHECK (
        completion_date IS NULL OR completion_date >= start_date
    )
);

-- Индексы для requests
CREATE INDEX idx_requests_status ON requests(request_status);
CREATE INDEX idx_requests_master ON requests(master_id);
CREATE INDEX idx_requests_client ON requests(client_id);
CREATE INDEX idx_requests_start_date ON requests(start_date);
CREATE INDEX idx_requests_completion_date ON requests(completion_date);

-- ============================================================================
-- ТАБЛИЦА: comments (Комментарии к заявкам)
-- ============================================================================
CREATE TABLE comments (
    comment_id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    master_id INTEGER,
    request_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Внешние ключи
    CONSTRAINT fk_comments_master 
        FOREIGN KEY (master_id) REFERENCES users(user_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_comments_request 
        FOREIGN KEY (request_id) REFERENCES requests(request_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Индексы для comments
CREATE INDEX idx_comments_request ON comments(request_id);
CREATE INDEX idx_comments_master ON comments(master_id);
CREATE INDEX idx_comments_created ON comments(created_at);

-- ============================================================================
-- ТАБЛИЦА: quality_surveys (Опросы качества)
-- ============================================================================
CREATE TABLE quality_surveys (
    survey_id SERIAL PRIMARY KEY,
    request_id INTEGER UNIQUE NOT NULL,
    qr_code VARCHAR(500),
    survey_link VARCHAR(500),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Внешний ключ
    CONSTRAINT fk_surveys_request 
        FOREIGN KEY (request_id) REFERENCES requests(request_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Индексы для quality_surveys
CREATE INDEX idx_surveys_request ON quality_surveys(request_id);
CREATE INDEX idx_surveys_rating ON quality_surveys(rating);

-- ============================================================================
-- ТАБЛИЦА: request_logs (Журнал изменений заявок)
-- ============================================================================
CREATE TABLE request_logs (
    log_id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL,
    user_id INTEGER,
    action_type VARCHAR(50) NOT NULL,
    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    old_value TEXT,
    new_value TEXT,
    
    -- Внешние ключи
    CONSTRAINT fk_logs_request 
        FOREIGN KEY (request_id) REFERENCES requests(request_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_logs_user 
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- Индексы для request_logs
CREATE INDEX idx_logs_request ON request_logs(request_id);
CREATE INDEX idx_logs_user ON request_logs(user_id);
CREATE INDEX idx_logs_action_date ON request_logs(action_date);

-- ============================================================================
-- ПРЕДСТАВЛЕНИЯ (VIEWS)
-- ============================================================================

-- Представление: Полная информация по заявкам
CREATE OR REPLACE VIEW v_requests_full AS
SELECT 
    r.request_id,
    r.start_date,
    r.car_type,
    r.car_model,
    r.problem_description,
    r.request_status,
    r.completion_date,
    r.repair_parts,
    m.fio AS master_fio,
    m.phone AS master_phone,
    c.fio AS client_fio,
    c.phone AS client_phone,
    r.created_at,
    r.updated_at
FROM requests r
LEFT JOIN users m ON r.master_id = m.user_id
LEFT JOIN users c ON r.client_id = c.user_id;

-- Представление: Статистика по механикам
CREATE OR REPLACE VIEW v_mechanic_statistics AS
SELECT 
    u.user_id,
    u.fio,
    COUNT(r.request_id) AS total_requests,
    COUNT(CASE WHEN r.request_status = 'Завершена' THEN 1 END) AS completed_requests,
    COUNT(CASE WHEN r.request_status = 'В процессе ремонта' THEN 1 END) AS in_progress_requests,
    ROUND(AVG(EXTRACT(DAY FROM (r.completion_date - r.start_date))), 2) AS avg_repair_days
FROM users u
LEFT JOIN requests r ON u.user_id = r.master_id
WHERE u.type = 'Автомеханик'
GROUP BY u.user_id, u.fio;

-- Представление: Статистика по статусам заявок
CREATE OR REPLACE VIEW v_request_status_statistics AS
SELECT 
    request_status,
    COUNT(*) AS request_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS percentage
FROM requests
GROUP BY request_status
ORDER BY request_count DESC;

-- ============================================================================
-- ТРИГГЕРЫ (Автоматическое обновление updated_at)
-- ============================================================================

-- Функция для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для users
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Триггер для requests
CREATE TRIGGER trg_requests_updated_at
    BEFORE UPDATE ON requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ФУНКЦИИ
-- ============================================================================

-- Функция: Расчёт среднего времени ремонта
CREATE OR REPLACE FUNCTION fn_get_average_repair_time()
RETURNS NUMERIC AS $$
DECLARE
    avg_time NUMERIC;
BEGIN
    SELECT ROUND(AVG(EXTRACT(DAY FROM (completion_date - start_date))), 2)
    INTO avg_time
    FROM requests
    WHERE completion_date IS NOT NULL 
      AND request_status IN ('Завершена', 'Готова к выдаче');
    
    RETURN COALESCE(avg_time, 0);
END;
$$ LANGUAGE plpgsql;

-- Функция: Получение статистики по заявкам
CREATE OR REPLACE FUNCTION fn_get_request_statistics()
RETURNS TABLE (
    total_requests INTEGER,
    completed_requests INTEGER,
    in_progress_requests INTEGER,
    new_requests INTEGER,
    avg_repair_time NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER,
        COUNT(CASE WHEN request_status = 'Завершена' THEN 1 END)::INTEGER,
        COUNT(CASE WHEN request_status = 'В процессе ремонта' THEN 1 END)::INTEGER,
        COUNT(CASE WHEN request_status = 'Новая заявка' THEN 1 END)::INTEGER,
        fn_get_average_repair_time();
    FROM requests;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- КОММЕНТАРИИ К ОБЪЕКТАМ
-- ============================================================================

COMMENT ON DATABASE auto_service IS 'База данных для учёта заявок на ремонт автомобилей';

COMMENT ON TABLE users IS 'Пользователи системы автосервиса';
COMMENT ON COLUMN users.type IS 'Роль пользователя: Менеджер, Автомеханик, Оператор, Заказчик, Менеджер по качеству';

COMMENT ON TABLE requests IS 'Заявки на ремонт автомобилей';
COMMENT ON COLUMN requests.request_status IS 'Статус заявки: Новая, В процессе, Готова к выдаче, Завершена, Ожидание запчастей';

COMMENT ON TABLE comments IS 'Комментарии механиков к заявкам';
COMMENT ON TABLE quality_surveys IS 'Опросы качества обслуживания клиентов';
COMMENT ON TABLE request_logs IS 'Журнал изменений заявок для аудита';