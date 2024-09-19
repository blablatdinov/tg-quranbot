-- The MIT License (MIT)
-- Copyright (c) 2018-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

-- Init migration.
-- depends:

CREATE TABLE public.admin_messages (
    key character varying NOT NULL,
    text character varying
);


CREATE TABLE public.ayats (
    ayat_id integer NOT NULL,
    public_id character varying NOT NULL,
    day integer,
    sura_id integer NOT NULL,
    audio_id character varying NOT NULL,
    ayat_number character varying(10) NOT NULL,
    content character varying NOT NULL,
    arab_text character varying NOT NULL,
    transliteration character varying NOT NULL
);

CREATE SEQUENCE public.ayats_ayat_id_seq
AS integer
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;

ALTER SEQUENCE public.ayats_ayat_id_seq OWNED BY public.ayats.ayat_id;

CREATE TABLE public.cities (
    city_id character varying NOT NULL,
    name character varying
);

CREATE TABLE public.favorite_ayats (
    ayat_id integer NOT NULL,
    user_id integer NOT NULL
);

CREATE TABLE public.files (
    file_id character varying NOT NULL,
    telegram_file_id character varying,
    link character varying,
    created_at timestamp without time zone NOT NULL
);

CREATE TABLE public.podcasts (
    podcast_id character varying NOT NULL,
    file_id character varying,
    article_link character varying
);

CREATE TABLE public.prayer_days (
    date date NOT NULL
);

CREATE TABLE public.prayers (
    prayer_id integer NOT NULL,
    name character varying,
    time time without time zone NOT NULL,
    city_id character varying,
    day_id date
);

CREATE TABLE public.prayers_at_user (
    prayer_at_user_id integer NOT NULL,
    public_id character varying,
    user_id integer NOT NULL,
    prayer_id integer,
    is_read boolean,
    prayer_group_id character varying
);

CREATE TABLE public.prayers_at_user_groups (
    prayers_at_user_group_id character varying NOT NULL
);

CREATE SEQUENCE public.prayers_at_user_prayer_at_user_id_seq
AS integer
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;

ALTER SEQUENCE public.prayers_at_user_prayer_at_user_id_seq OWNED BY public.prayers_at_user.prayer_at_user_id;

CREATE SEQUENCE public.prayers_prayer_id_seq
AS integer
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;

ALTER SEQUENCE public.prayers_prayer_id_seq OWNED BY public.prayers.prayer_id;

CREATE TABLE public.suras (
    sura_id integer NOT NULL,
    link character varying NOT NULL
);

CREATE SEQUENCE public.suras_sura_id_seq
AS integer
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;

ALTER SEQUENCE public.suras_sura_id_seq OWNED BY public.suras.sura_id;


CREATE TABLE public.users (
    chat_id bigint NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    comment character varying,
    day integer,
    city_id character varying,
    referrer_id integer,
    legacy_id integer
);

ALTER TABLE ONLY public.ayats ALTER COLUMN ayat_id SET DEFAULT nextval('public.ayats_ayat_id_seq'::regclass);

ALTER TABLE ONLY public.prayers ALTER COLUMN prayer_id SET DEFAULT nextval('public.prayers_prayer_id_seq'::regclass);

ALTER TABLE ONLY public.prayers_at_user ALTER COLUMN prayer_at_user_id SET DEFAULT nextval(
    'public.prayers_at_user_prayer_at_user_id_seq'::regclass
);

ALTER TABLE ONLY public.suras ALTER COLUMN sura_id SET DEFAULT nextval('public.suras_sura_id_seq'::regclass);

ALTER TABLE ONLY public.admin_messages
ADD CONSTRAINT admin_messages_pkey PRIMARY KEY (key);

ALTER TABLE ONLY public.ayats
ADD CONSTRAINT ayats_pkey PRIMARY KEY (ayat_id);

ALTER TABLE ONLY public.cities
ADD CONSTRAINT cities_pkey PRIMARY KEY (city_id);

ALTER TABLE ONLY public.favorite_ayats
ADD CONSTRAINT favorite_ayats_pkey PRIMARY KEY (ayat_id, user_id);

ALTER TABLE ONLY public.files
ADD CONSTRAINT files_pkey PRIMARY KEY (file_id);

ALTER TABLE ONLY public.podcasts
ADD CONSTRAINT podcasts_pkey PRIMARY KEY (podcast_id);

ALTER TABLE ONLY public.prayer_days
ADD CONSTRAINT prayer_days_pkey PRIMARY KEY (date);

ALTER TABLE ONLY public.prayers_at_user_groups
ADD CONSTRAINT prayers_at_user_groups_pkey PRIMARY KEY (prayers_at_user_group_id);

ALTER TABLE ONLY public.prayers_at_user
ADD CONSTRAINT prayers_at_user_pkey PRIMARY KEY (prayer_at_user_id);

ALTER TABLE ONLY public.prayers
ADD CONSTRAINT prayers_pkey PRIMARY KEY (prayer_id);

ALTER TABLE ONLY public.suras
ADD CONSTRAINT suras_pkey PRIMARY KEY (sura_id);

ALTER TABLE ONLY public.users
ADD CONSTRAINT users_pkey PRIMARY KEY (chat_id);

ALTER TABLE ONLY public.ayats
ADD CONSTRAINT ayats_audio_id_fkey FOREIGN KEY (audio_id) REFERENCES public.files (file_id);

ALTER TABLE ONLY public.ayats
ADD CONSTRAINT ayats_sura_id_fkey FOREIGN KEY (sura_id) REFERENCES public.suras (sura_id);

ALTER TABLE ONLY public.favorite_ayats
ADD CONSTRAINT favorite_ayats_ayat_id_fkey FOREIGN KEY (ayat_id) REFERENCES public.ayats (ayat_id);

ALTER TABLE ONLY public.favorite_ayats
ADD CONSTRAINT favorite_ayats_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users (chat_id);

ALTER TABLE ONLY public.podcasts
ADD CONSTRAINT podcasts_file_id_fkey FOREIGN KEY (file_id) REFERENCES public.files (file_id);

ALTER TABLE ONLY public.prayers_at_user
ADD CONSTRAINT prayers_at_user_prayer_group_id_fkey FOREIGN KEY (
    prayer_group_id
) REFERENCES public.prayers_at_user_groups (prayers_at_user_group_id);

ALTER TABLE ONLY public.prayers_at_user
ADD CONSTRAINT prayers_at_user_prayer_id_fkey FOREIGN KEY (prayer_id) REFERENCES public.prayers (prayer_id);

ALTER TABLE ONLY public.prayers_at_user
ADD CONSTRAINT prayers_at_user_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users (chat_id);

ALTER TABLE ONLY public.prayers
ADD CONSTRAINT prayers_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities (city_id);

ALTER TABLE ONLY public.prayers
ADD CONSTRAINT prayers_day_id_fkey FOREIGN KEY (day_id) REFERENCES public.prayer_days (date);

ALTER TABLE ONLY public.users
ADD CONSTRAINT users_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities (city_id);

ALTER TABLE ONLY public.users
ADD CONSTRAINT users_referrer_id_fkey FOREIGN KEY (referrer_id) REFERENCES public.users (chat_id);
