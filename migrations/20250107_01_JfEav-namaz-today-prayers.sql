-- SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
-- SPDX-License-Identifier: MIT

-- Namaz today prayers
-- depends: 20240930_01_pdRsM-ru-ayat-sound

ALTER TABLE cities ADD CONSTRAINT cities_uniq_name UNIQUE (name);

CREATE TABLE namaz_today_cities (
    city_id character varying,
    link character varying
);

ALTER TABLE ONLY public.namaz_today_cities
ADD CONSTRAINT namaz_today_cities_pkey PRIMARY KEY (city_id);

ALTER TABLE ONLY public.namaz_today_cities
ADD CONSTRAINT namaz_today_cities_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities (city_id);
