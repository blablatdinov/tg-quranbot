-- Change chat_id type
-- depends: 20230815_01_7ALQG
ALTER TABLE users ALTER COLUMN chat_id TYPE bigint USING chat_id::bigint;
ALTER TABLE prayers_at_user ALTER COLUMN user_id TYPE bigint USING user_id::bigint;
