-- ============================================================================
-- ПОЛЬЗОВАТЕЛИ БД И ПРАВА ДОСТУПА
-- ============================================================================

-- Создание групп ролей
CREATE ROLE auto_admins;      -- Администраторы БД
CREATE ROLE auto_managers;    -- Менеджеры автосервиса
CREATE ROLE auto_mechanics;   -- Автомеханики
CREATE ROLE auto_operators;   -- Операторы
CREATE ROLE auto_clients;     -- Клиенты (только просмотр своих заявок)

-- ============================================================================
-- ПРАВА ДЛЯ ГРУПП
-- ============================================================================

-- Администраторы: полный доступ
GRANT ALL PRIVILEGES ON DATABASE auto_service TO auto_admins;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO auto_admins;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO auto_admins;

-- Менеджеры: чтение всех таблиц, запись в requests и comments
GRANT CONNECT ON DATABASE auto_service TO auto_managers;
GRANT USAGE ON SCHEMA public TO auto_managers;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO auto_managers;
GRANT INSERT, UPDATE ON requests, comments, request_logs TO auto_managers;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO auto_managers;

-- Автомеханики: чтение заявок, запись комментариев, обновление своих заявок
GRANT CONNECT ON DATABASE auto_service TO auto_mechanics;
GRANT USAGE ON SCHEMA public TO auto_mechanics;
GRANT SELECT ON requests, users, comments TO auto_mechanics;
GRANT INSERT ON comments TO auto_mechanics;
GRANT UPDATE (request_status, repair_parts, completion_date, master_id) ON requests TO auto_mechanics;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO auto_mechanics;

-- Операторы: создание заявок, чтение, назначение механиков
GRANT CONNECT ON DATABASE auto_service TO auto_operators;
GRANT USAGE ON SCHEMA public TO auto_operators;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO auto_operators;
GRANT INSERT, UPDATE ON requests TO auto_operators;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO auto_operators;

-- Клиенты: только просмотр своих заявок
GRANT CONNECT ON DATABASE auto_service TO auto_clients;
GRANT USAGE ON SCHEMA public TO auto_clients;
GRANT SELECT ON v_requests_full TO auto_clients;
REVOKE ALL ON users, comments, quality_surveys, request_logs FROM auto_clients;

-- ============================================================================
-- ПОЛЬЗОВАТЕЛИ БД (для подключения приложения)
-- ============================================================================

-- Пользователь для приложения (полный доступ)
CREATE USER auto_app WITH PASSWORD 'AutoApp2024!';
GRANT auto_admins TO auto_app;

-- Пользователь для менеджера
CREATE USER auto_manager_user WITH PASSWORD 'Manager2024!';
GRANT auto_managers TO auto_manager_user;

-- Пользователь для механика
CREATE USER auto_mechanic_user WITH PASSWORD 'Mechanic2024!';
GRANT auto_mechanics TO auto_mechanic_user;

-- Пользователь для оператора
CREATE USER auto_operator_user WITH PASSWORD 'Operator2024!';
GRANT auto_operators TO auto_operator_user;

-- ============================================================================
-- ROW LEVEL SECURITY (Безопасность на уровне строк)
-- ============================================================================

-- Включение RLS для таблицы requests
ALTER TABLE requests ENABLE ROW LEVEL SECURITY;

-- Политика: Механики видят только свои заявки
CREATE POLICY mechanic_own_requests ON requests
    FOR ALL
    TO auto_mechanics
    USING (master_id = (SELECT user_id FROM users WHERE login = current_user))
    WITH CHECK (master_id = (SELECT user_id FROM users WHERE login = current_user));

-- Политика: Менеджеры видят все заявки
CREATE POLICY manager_all_requests ON requests
    FOR ALL
    TO auto_managers
    USING (TRUE)
    WITH CHECK (TRUE);

-- ============================================================================
-- ПРОВЕРКА ПРАВ
-- ============================================================================

-- Показать права для таблицы
\dp users
\dp requests
\dp comments

-- Показать пользователей
\du