-- SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
-- SPDX-License-Identifier: MIT

-- Remove defaults
-- depends: 20240607_01_PlBa5-prayer-at-user-unique-together

ALTER TABLE users ALTER COLUMN is_active SET DEFAULT true;
