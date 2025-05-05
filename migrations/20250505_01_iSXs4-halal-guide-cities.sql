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

-- halal guide cities
-- depends: 20250108_02_3qKdF-prayers-unique

-- # TODO: #1678:30min заполнить таблицу данными из https://halalguide.me/sitemap-namaz.xml

CREATE TABLE halal_guide_cities (
    city_id character varying,
    link character varying
);

ALTER TABLE ONLY public.halal_guide_cities
ADD CONSTRAINT halal_guide_cities_pkey PRIMARY KEY (city_id);

ALTER TABLE ONLY public.halal_guide_cities
ADD CONSTRAINT halal_guide_cities_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities (city_id);
