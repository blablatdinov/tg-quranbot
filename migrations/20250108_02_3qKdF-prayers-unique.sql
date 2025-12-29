-- SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
-- SPDX-License-Identifier: MIT

-- Prayers unique
-- depends: 20250107_01_JfEav-namaz-today-prayers

DELETE FROM prayers
WHERE prayer_id IN (
    SELECT unnest(subquery.ids_for_remove) FROM
        (
            SELECT
                (array_agg(prayers.prayer_id))[2:] AS ids_for_remove,
                count(*) AS records_count
            FROM prayers
            GROUP BY prayers.city_id, prayers.day
            HAVING count(*) > 1
        ) AS subquery
);

ALTER TABLE prayers
ADD CONSTRAINT prayers_unique UNIQUE (city_id, name, day);
