-- SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
-- SPDX-License-Identifier: MIT

-- Remove days table. Step 1
-- depends: 20230826_01_RChAw-change-chat-id-type

ALTER TABLE prayers ADD COLUMN day date;

UPDATE prayers
SET day = day_id;
