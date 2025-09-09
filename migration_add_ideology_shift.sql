-- Миграция для добавления поля ideology_shift в таблицу actions
-- Выполнить после обновления кода

-- Добавляем поле ideology_shift
ALTER TABLE actions ADD COLUMN ideology_shift INTEGER;

-- Добавляем ограничение на диапазон значений
ALTER TABLE actions ADD CONSTRAINT ck_actions_ideology_shift_range 
    CHECK (ideology_shift >= -1 AND ideology_shift <= 1);

-- Комментарий к полю
COMMENT ON COLUMN actions.ideology_shift IS 'Направление изменения идеологии политика: -1 (влево), 0 (не изменять), 1 (вправо)';
