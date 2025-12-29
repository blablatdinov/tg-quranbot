-- SPDX-FileCopyrightText: Copyright (c) 2018-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
-- SPDX-License-Identifier: MIT

-- halal guide cities
-- depends: 20250108_02_3qKdF-prayers-unique

CREATE TABLE halal_guide_cities (
    city_id character varying,
    link character varying
);

ALTER TABLE ONLY public.halal_guide_cities
ADD CONSTRAINT halal_guide_cities_pkey PRIMARY KEY (city_id);

ALTER TABLE ONLY public.halal_guide_cities
ADD CONSTRAINT halal_guide_cities_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities (city_id);
