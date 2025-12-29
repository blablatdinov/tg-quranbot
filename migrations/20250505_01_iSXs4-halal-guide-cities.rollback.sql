-- SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
-- SPDX-License-Identifier: MIT

-- halal guide cities
-- depends: 20250108_02_3qKdF-prayers-unique

ALTER TABLE ONLY public.halal_guide_cities
DROP CONSTRAINT namaz_today_cities_city_id_fkey;

ALTER TABLE ONLY public.halal_guide_cities
DROP CONSTRAINT namaz_today_cities_pkey;

DROP TABLE IF EXISTS public.halal_guide_cities;
