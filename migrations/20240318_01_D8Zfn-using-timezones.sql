-- Using timezones
-- depends: 20230915_01_Cv22v-podcast-reactions

ALTER TABLE public.files
ALTER COLUMN created_at SET DATA TYPE timestamp with time zone;
