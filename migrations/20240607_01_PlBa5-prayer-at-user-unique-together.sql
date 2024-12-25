-- The MIT License (MIT)
--
-- Copyright (c) 2018-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
--
-- Permission is hereby granted, free of charge, to any person obtaining a copy
-- of this software and associated documentation files (the "Software"), to deal
-- in the Software without restriction, including without limitation the rights
-- to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
-- copies of the Software, and to permit persons to whom the Software is
-- furnished to do so, subject to the following conditions:
--
-- The above copyright notice and this permission notice shall be included in all
-- copies or substantial portions of the Software.
--
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
-- EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
-- MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
-- IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
-- DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
-- OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
-- OR OTHER DEALINGS IN THE SOFTWARE.

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
