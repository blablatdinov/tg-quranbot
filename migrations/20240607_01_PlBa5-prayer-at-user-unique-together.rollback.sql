-- SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
-- SPDX-License-Identifier: MIT

-- Prayer at user unique together
-- depends: 20240318_01_D8Zfn-using-timezones

ALTER TABLE prayers_at_user
DROP CONSTRAINT prayers_at_user_user_id_prayer_id_key;
