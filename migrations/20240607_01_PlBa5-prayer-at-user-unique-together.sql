-- SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
-- SPDX-License-Identifier: MIT

-- Prayer at user unique together
-- depends: 20240318_01_D8Zfn-using-timezones

DELETE FROM prayers_at_user
WHERE prayer_at_user_id IN (
    SELECT unnest(subquery.ids_for_remove) FROM
        (
            SELECT
                (array_agg(prayers_at_user.prayer_at_user_id))[2:] AS ids_for_remove,
                count(*) AS records_count
            FROM prayers_at_user
            GROUP BY prayers_at_user.user_id, prayers_at_user.prayer_id
            HAVING count(*) > 1
        ) AS subquery
);

ALTER TABLE prayers_at_user
ADD UNIQUE (user_id, prayer_id);
