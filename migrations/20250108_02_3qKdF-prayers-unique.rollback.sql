-- SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
-- SPDX-License-Identifier: MIT

-- Prayers unique
-- depends: 20250107_01_JfEav-namaz-today-prayers

ALTER TABLE prayers
DROP CONSTRAINT IF EXISTS prayers_unique;
