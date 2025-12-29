-- SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
-- SPDX-License-Identifier: MIT

-- remove days table. step 3
-- depends: 20230830_01_neA0R-remove-days-table-step-1

ALTER TABLE prayers ALTER COLUMN day SET NOT NULL;

ALTER TABLE prayers DROP COLUMN day_id;

ALTER TABLE prayer_days DROP CONSTRAINT prayer_days_pkey;

DROP TABLE prayer_days;
