CREATE TABLE num_val_percentage
(
    id SERIAL PRIMARY KEY,
    percentage NUMERIC(10, 2) NOT NULL
);

INSERT INTO num_val_percentage
SELECT
	trips.id,
	ROUND((num_val::NUMERIC / (SELECT MAX(num_val) FROM trips)) * 100, 2) AS percentage
FROM
	trips;