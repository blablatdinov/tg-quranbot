--
-- PostgreSQL database dump
--

-- Dumped from database version 13.11
-- Dumped by pg_dump version 13.11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admin_messages; Type: TABLE; Schema: public; Owner: almazilaletdinov
--

CREATE TABLE public.admin_messages (
    key character varying NOT NULL,
    text character varying
);


ALTER TABLE public.admin_messages OWNER TO almazilaletdinov;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: almazilaletdinov
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO almazilaletdinov;

--
-- Name: ayats; Type: TABLE; Schema: public; Owner: almazilaletdinov
--

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


ALTER TABLE public.ayats OWNER TO almazilaletdinov;

--
-- Name: ayats_ayat_id_seq; Type: SEQUENCE; Schema: public; Owner: almazilaletdinov
--

CREATE SEQUENCE public.ayats_ayat_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ayats_ayat_id_seq OWNER TO almazilaletdinov;

--
-- Name: ayats_ayat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: almazilaletdinov
--

ALTER SEQUENCE public.ayats_ayat_id_seq OWNED BY public.ayats.ayat_id;


--
-- Name: cities; Type: TABLE; Schema: public; Owner: almazilaletdinov
--

CREATE TABLE public.cities (
    city_id character varying NOT NULL,
    name character varying
);


ALTER TABLE public.cities OWNER TO almazilaletdinov;

--
-- Name: favorite_ayats; Type: TABLE; Schema: public; Owner: almazilaletdinov
--

CREATE TABLE public.favorite_ayats (
    ayat_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.favorite_ayats OWNER TO almazilaletdinov;

--
-- Name: files; Type: TABLE; Schema: public; Owner: almazilaletdinov
--

CREATE TABLE public.files (
    file_id character varying NOT NULL,
    telegram_file_id character varying,
    link character varying,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.files OWNER TO almazilaletdinov;

--
-- Name: podcasts; Type: TABLE; Schema: public; Owner: almazilaletdinov
--

CREATE TABLE public.podcasts (
    podcast_id character varying NOT NULL,
    file_id character varying,
    article_link character varying
);


ALTER TABLE public.podcasts OWNER TO almazilaletdinov;

--
-- Name: prayer_days; Type: TABLE; Schema: public; Owner: almazilaletdinov
--

CREATE TABLE public.prayer_days (
    date date NOT NULL
);


ALTER TABLE public.prayer_days OWNER TO almazilaletdinov;

--
-- Name: prayers; Type: TABLE; Schema: public; Owner: almazilaletdinov
--

CREATE TABLE public.prayers (
    prayer_id integer NOT NULL,
    name character varying,
    "time" time without time zone NOT NULL,
    city_id character varying,
    day_id date
);


ALTER TABLE public.prayers OWNER TO almazilaletdinov;

--
-- Name: prayers_at_user; Type: TABLE; Schema: public; Owner: almazilaletdinov
--

CREATE TABLE public.prayers_at_user (
    prayer_at_user_id integer NOT NULL,
    public_id character varying,
    user_id integer NOT NULL,
    prayer_id integer,
    is_read boolean,
    prayer_group_id character varying
);


ALTER TABLE public.prayers_at_user OWNER TO almazilaletdinov;

--
-- Name: prayers_at_user_groups; Type: TABLE; Schema: public; Owner: almazilaletdinov
--

CREATE TABLE public.prayers_at_user_groups (
    prayers_at_user_group_id character varying NOT NULL
);


ALTER TABLE public.prayers_at_user_groups OWNER TO almazilaletdinov;

--
-- Name: prayers_at_user_prayer_at_user_id_seq; Type: SEQUENCE; Schema: public; Owner: almazilaletdinov
--

CREATE SEQUENCE public.prayers_at_user_prayer_at_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.prayers_at_user_prayer_at_user_id_seq OWNER TO almazilaletdinov;

--
-- Name: prayers_at_user_prayer_at_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: almazilaletdinov
--

ALTER SEQUENCE public.prayers_at_user_prayer_at_user_id_seq OWNED BY public.prayers_at_user.prayer_at_user_id;


--
-- Name: prayers_prayer_id_seq; Type: SEQUENCE; Schema: public; Owner: almazilaletdinov
--

CREATE SEQUENCE public.prayers_prayer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.prayers_prayer_id_seq OWNER TO almazilaletdinov;

--
-- Name: prayers_prayer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: almazilaletdinov
--

ALTER SEQUENCE public.prayers_prayer_id_seq OWNED BY public.prayers.prayer_id;


--
-- Name: suras; Type: TABLE; Schema: public; Owner: almazilaletdinov
--

CREATE TABLE public.suras (
    sura_id integer NOT NULL,
    link character varying NOT NULL
);


ALTER TABLE public.suras OWNER TO almazilaletdinov;

--
-- Name: suras_sura_id_seq; Type: SEQUENCE; Schema: public; Owner: almazilaletdinov
--

CREATE SEQUENCE public.suras_sura_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.suras_sura_id_seq OWNER TO almazilaletdinov;

--
-- Name: suras_sura_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: almazilaletdinov
--

ALTER SEQUENCE public.suras_sura_id_seq OWNED BY public.suras.sura_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: almazilaletdinov
--

CREATE TABLE public.users (
    chat_id bigint NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    comment character varying,
    day integer,
    city_id character varying,
    referrer_id integer,
    legacy_id integer
);


ALTER TABLE public.users OWNER TO almazilaletdinov;

--
-- Name: ayats ayat_id; Type: DEFAULT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.ayats ALTER COLUMN ayat_id SET DEFAULT nextval('public.ayats_ayat_id_seq'::regclass);


--
-- Name: prayers prayer_id; Type: DEFAULT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.prayers ALTER COLUMN prayer_id SET DEFAULT nextval('public.prayers_prayer_id_seq'::regclass);


--
-- Name: prayers_at_user prayer_at_user_id; Type: DEFAULT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.prayers_at_user ALTER COLUMN prayer_at_user_id SET DEFAULT nextval('public.prayers_at_user_prayer_at_user_id_seq'::regclass);


--
-- Name: suras sura_id; Type: DEFAULT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.suras ALTER COLUMN sura_id SET DEFAULT nextval('public.suras_sura_id_seq'::regclass);


--
-- Name: admin_messages admin_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.admin_messages
    ADD CONSTRAINT admin_messages_pkey PRIMARY KEY (key);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: ayats ayats_pkey; Type: CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.ayats
    ADD CONSTRAINT ayats_pkey PRIMARY KEY (ayat_id);


--
-- Name: cities cities_pkey; Type: CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT cities_pkey PRIMARY KEY (city_id);


--
-- Name: favorite_ayats favorite_ayats_pkey; Type: CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.favorite_ayats
    ADD CONSTRAINT favorite_ayats_pkey PRIMARY KEY (ayat_id, user_id);


--
-- Name: files files_pkey; Type: CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.files
    ADD CONSTRAINT files_pkey PRIMARY KEY (file_id);


--
-- Name: podcasts podcasts_pkey; Type: CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.podcasts
    ADD CONSTRAINT podcasts_pkey PRIMARY KEY (podcast_id);


--
-- Name: prayer_days prayer_days_pkey; Type: CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.prayer_days
    ADD CONSTRAINT prayer_days_pkey PRIMARY KEY (date);


--
-- Name: prayers_at_user_groups prayers_at_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.prayers_at_user_groups
    ADD CONSTRAINT prayers_at_user_groups_pkey PRIMARY KEY (prayers_at_user_group_id);


--
-- Name: prayers_at_user prayers_at_user_pkey; Type: CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.prayers_at_user
    ADD CONSTRAINT prayers_at_user_pkey PRIMARY KEY (prayer_at_user_id);


--
-- Name: prayers prayers_pkey; Type: CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.prayers
    ADD CONSTRAINT prayers_pkey PRIMARY KEY (prayer_id);


--
-- Name: suras suras_pkey; Type: CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.suras
    ADD CONSTRAINT suras_pkey PRIMARY KEY (sura_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (chat_id);


--
-- Name: ayats ayats_audio_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.ayats
    ADD CONSTRAINT ayats_audio_id_fkey FOREIGN KEY (audio_id) REFERENCES public.files(file_id);


--
-- Name: ayats ayats_sura_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.ayats
    ADD CONSTRAINT ayats_sura_id_fkey FOREIGN KEY (sura_id) REFERENCES public.suras(sura_id);


--
-- Name: favorite_ayats favorite_ayats_ayat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.favorite_ayats
    ADD CONSTRAINT favorite_ayats_ayat_id_fkey FOREIGN KEY (ayat_id) REFERENCES public.ayats(ayat_id);


--
-- Name: favorite_ayats favorite_ayats_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.favorite_ayats
    ADD CONSTRAINT favorite_ayats_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(chat_id);


--
-- Name: podcasts podcasts_file_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.podcasts
    ADD CONSTRAINT podcasts_file_id_fkey FOREIGN KEY (file_id) REFERENCES public.files(file_id);


--
-- Name: prayers_at_user prayers_at_user_prayer_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.prayers_at_user
    ADD CONSTRAINT prayers_at_user_prayer_group_id_fkey FOREIGN KEY (prayer_group_id) REFERENCES public.prayers_at_user_groups(prayers_at_user_group_id);


--
-- Name: prayers_at_user prayers_at_user_prayer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.prayers_at_user
    ADD CONSTRAINT prayers_at_user_prayer_id_fkey FOREIGN KEY (prayer_id) REFERENCES public.prayers(prayer_id);


--
-- Name: prayers_at_user prayers_at_user_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.prayers_at_user
    ADD CONSTRAINT prayers_at_user_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(chat_id);


--
-- Name: prayers prayers_city_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.prayers
    ADD CONSTRAINT prayers_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities(city_id);


--
-- Name: prayers prayers_day_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.prayers
    ADD CONSTRAINT prayers_day_id_fkey FOREIGN KEY (day_id) REFERENCES public.prayer_days(date);


--
-- Name: users users_city_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities(city_id);


--
-- Name: users users_referrer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: almazilaletdinov
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_referrer_id_fkey FOREIGN KEY (referrer_id) REFERENCES public.users(chat_id);


--
-- PostgreSQL database dump complete
--

