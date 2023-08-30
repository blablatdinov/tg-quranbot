-- remove days table. step 3
-- depends: 20230830_01_neA0R-remove-days-table-step-1

CREATE TABLE prayer_days (
    date date NOT NULL
);

ALTER TABLE ONLY prayer_days ADD CONSTRAINT prayer_days_pkey PRIMARY KEY (date);

ALTER TABLE prayers ADD COLUMN day_id date;
UPDATE prayers SET day_id = day;

INSERT INTO prayer_days (date)
SELECT datetime::date
FROM generate_series(
    '2019-12-01'::date,
    '2023-12-31'::date,
    '1 day'::interval
) AS datetime;
SELECT * FROM prayer_days;

ALTER TABLE ONLY prayers ADD CONSTRAINT prayers_day_id_fkey FOREIGN KEY (day_id) REFERENCES prayer_days (date);
