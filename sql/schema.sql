CREATE TABLE metrics (
metric_id INTEGER PRIMARY KEY,
metric_name VARCHAR(100)
);

CREATE TABLE geography (
geography_id INTEGER PRIMARY KEY,
area_code VARCHAR(20),
area_name VARCHAR(100)
);

CREATE TABLE industry (
industry_id INTEGER PRIMARY KEY,
industry_code VARCHAR(20),
industry_name VARCHAR(100)
);

CREATE TABLE demographics (
demographic_id INTEGER PRIMARY KEY,
gender VARCHAR(50),
age_group VARCHAR(50)
);

CREATE TABLE series (
series_id VARCHAR(50) PRIMARY KEY,
metric_id INTEGER,
geography_id INTEGER,
industry_id INTEGER,
demographic_id INTEGER,

```
CONSTRAINT fk_metric
    FOREIGN KEY (metric_id)
    REFERENCES metrics(metric_id),

CONSTRAINT fk_geography
    FOREIGN KEY (geography_id)
    REFERENCES geography(geography_id),

CONSTRAINT fk_industry
    FOREIGN KEY (industry_id)
    REFERENCES industry(industry_id),

CONSTRAINT fk_demographics
    FOREIGN KEY (demographic_id)
    REFERENCES demographics(demographic_id)
```

);

CREATE TABLE observations (
series_id VARCHAR(50),
year INTEGER,
period VARCHAR(10),
value NUMERIC,

```
PRIMARY KEY (series_id, year, period),

CONSTRAINT fk_series
    FOREIGN KEY (series_id)
    REFERENCES series(series_id)
```

);
