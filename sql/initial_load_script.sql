INSERT INTO metrics (metric_id, metric_name)
VALUES
(1, 'Unemployment Rate'),
(2, 'Employment Level'),
(3, 'Labor Force');

INSERT INTO geography (geography_id, area_code, area_name)
VALUES
(1, '31140', 'Louisville/Jefferson County, KY-IN Metropolitan Area'),
(2, '21', 'Kentucky');

INSERT INTO industry (industry_id, industry_code, industry_name)
VALUES
(1, '30000000', 'Manufacturing'),
(2, '42000000', 'Retail Trade'),
(3, '43400089', 'Transportation and Warehousing'),
(4, '65000000', 'Private Education and Health Services'),
(5, '90000000', 'Government');

INSERT INTO demographics (demographic_id, gender, age_group)
VALUES
(1, 'All', 'All Ages');
