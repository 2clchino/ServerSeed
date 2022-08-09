DROP SCHEMA IF EXISTS derby;
CREATE SCHEMA derby;
USE derby;

DROP TABLE IF EXISTS horse;

CREATE TABLE horse
(
  id           INT(10),
  name     VARCHAR(40)
);