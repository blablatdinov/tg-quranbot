-- Podcast reactions
-- depends: 20230830_02_QXaRV-remove-days-table-step-3

ALTER TABLE public.podcasts
ADD COLUMN public_id character varying;

UPDATE public.podcasts
SET public_id = podcast_id;

ALTER TABLE public.podcasts
DROP COLUMN podcast_id;

ALTER TABLE public.podcasts
ADD COLUMN podcast_id serial PRIMARY KEY;

CREATE TABLE public.podcast_reactions (
    podcast_id bigint NOT NULL,
    user_id bigint NOT NULL,
    reaction character varying(10) NOT NULL
);

ALTER TABLE ONLY public.podcast_reactions
ADD CONSTRAINT podcast_reactions_pkey PRIMARY KEY (podcast_id, user_id);

ALTER TABLE ONLY public.podcast_reactions
ADD CONSTRAINT podcast_reactions_ayat_id_fkey FOREIGN KEY (podcast_id) REFERENCES public.podcasts (podcast_id);

ALTER TABLE ONLY public.podcast_reactions
ADD CONSTRAINT podcast_reactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users (chat_id);
