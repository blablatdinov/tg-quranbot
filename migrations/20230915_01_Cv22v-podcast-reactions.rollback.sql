-- Podcast reactions
-- depends: 20230830_02_QXaRV-remove-days-table-step-3

DROP TABLE public.podcast_reactions;

ALTER TABLE public.podcasts
DROP COLUMN podcast_id;

ALTER TABLE public.podcasts
ADD COLUMN podcast_id character varying;

UPDATE public.podcasts
SET podcast_id = public_id;

ALTER TABLE public.podcasts
DROP COLUMN public_id;

ALTER TABLE ONLY public.podcasts
ADD CONSTRAINT podcasts_pkey PRIMARY KEY (podcast_id);

ALTER TABLE ONLY public.podcasts
ALTER COLUMN podcast_id SET NOT NULL;
