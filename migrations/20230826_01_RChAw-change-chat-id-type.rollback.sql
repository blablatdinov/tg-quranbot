-- Change chat_id type
-- depends: 20230815_01_7ALQG

ALTER TABLE favorite_ayats ALTER COLUMN user_id TYPE integer USING user_id::integer;

ALTER TABLE prayers_at_user ALTER COLUMN user_id TYPE integer USING user_id::integer;
