CREATE TABLE top_loaded_stations
(
	line_name VARCHAR(255),
	station_name VARCHAR(255),
	avg_num_val NUMERIC(10, 2) NOT NULL,
	PRIMARY KEY (line_name, station_name)
);

INSERT INTO top_loaded_stations
SELECT line_name, station_name, ROUND(AVG(num_val), 0) AS average_num_val
FROM trips
GROUP BY line_name, station_name
ORDER BY average_num_val DESC;
