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
