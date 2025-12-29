-- SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
-- SPDX-License-Identifier: MIT

-- Namaz today prayers
-- depends: 20240930_01_pdRsM-ru-ayat-sound

ALTER TABLE ONLY public.namaz_today_cities
DROP CONSTRAINT namaz_today_cities_city_id_fkey;

ALTER TABLE ONLY public.namaz_today_cities
DROP CONSTRAINT namaz_today_cities_pkey;

DROP TABLE IF EXISTS public.namaz_today_cities;

ALTER TABLE cities DROP CONSTRAINT IF EXISTS cities_uniq_name;
