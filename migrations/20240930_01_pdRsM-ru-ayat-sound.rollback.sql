-- SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
-- SPDX-License-Identifier: MIT

-- Ru ayat sound
-- depends: 20240706_01_VaxTE-remove-defaults

ALTER TABLE ayats RENAME COLUMN ar_audio_id TO audio_id;

ALTER TABLE ayats DROP COLUMN ru_audio_id;

ALTER TABLE ayats DROP CONSTRAINT ayats_ru_audio_id_fkey;
