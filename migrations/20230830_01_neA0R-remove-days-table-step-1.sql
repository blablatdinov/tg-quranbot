-- Remove days table. Step 1
-- depends: 20230826_01_RChAw-change-chat-id-type

ALTER TABLE prayers ADD COLUMN day date;

UPDATE prayers
SET day = day_id;
