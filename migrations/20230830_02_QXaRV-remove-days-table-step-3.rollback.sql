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

-- remove days table. step 3
-- depends: 20230830_01_neA0R-remove-days-table-step-1

CREATE TABLE prayer_days (
    date date NOT NULL  -- noqa: RF04
);

ALTER TABLE ONLY prayer_days ADD CONSTRAINT prayer_days_pkey PRIMARY KEY (date);

ALTER TABLE prayers ADD COLUMN day_id date;
UPDATE prayers SET day_id = day;

INSERT INTO prayer_days (date)
SELECT i::date
FROM generate_series(
    '2019-12-01'::date,
    '2023-12-31'::date,
    '1 day'::interval
) AS t (i);

ALTER TABLE ONLY prayers ADD CONSTRAINT prayers_day_id_fkey FOREIGN KEY (day_id) REFERENCES prayer_days (date);
