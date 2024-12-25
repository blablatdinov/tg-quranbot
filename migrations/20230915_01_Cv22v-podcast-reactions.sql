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
