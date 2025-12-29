-- SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
-- SPDX-License-Identifier: MIT

-- Change chat_id type
-- depends: 20230815_01_7ALQG

ALTER TABLE favorite_ayats ALTER COLUMN user_id TYPE integer USING user_id::integer;

ALTER TABLE prayers_at_user ALTER COLUMN user_id TYPE integer USING user_id::integer;
