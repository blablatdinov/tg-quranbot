-- SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
-- SPDX-License-Identifier: MIT

-- Ru ayat sound
-- depends: 20240706_01_VaxTE-remove-defaults

ALTER TABLE ayats RENAME COLUMN audio_id TO ar_audio_id;

ALTER TABLE ayats ADD COLUMN ru_audio_id character varying;

ALTER TABLE ONLY ayats
ADD CONSTRAINT ayats_ru_audio_id_fkey FOREIGN KEY (ru_audio_id) REFERENCES files (file_id);
