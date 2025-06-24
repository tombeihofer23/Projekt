-- Ensure the timescaledb extension is available
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- Create the sensor data table
CREATE TABLE IF NOT EXISTS sensor_data (
    timestamp   TIMESTAMPTZ       NOT NULL,
    box_id      TEXT              NOT NULL,
    sensor_id   TEXT              NOT NULL,
    measurement DOUBLE PRECISION, -- Use DOUBLE PRECISION for floating point values
    unit        TEXT,
    sensor_type TEXT,
    icon        TEXT,
    title       TEXT,
    -- Define composite primary key or unique constraint for ON CONFLICT
    UNIQUE (timestamp, box_id, sensor_id)
);

-- Create sensor metadata table
-- CREATE TABLE IF NOT EXISTS sensor_metadata AS
-- 	SELECT DISTINCT
-- 		sensor_id
-- 		,unit
-- 		,sensor_type
-- 		,icon
-- 		,title
-- 	FROM sensor_data;

-- Create the TimescaleDB hypertable, partitioning by time
-- if_not_exists prevents error if script is run multiple times
SELECT create_hypertable('sensor_data', 'timestamp', if_not_exists => TRUE);

-- Optional: Add indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_sensor_data_box_id_ts ON sensor_data (box_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_data_sensor_id_ts ON sensor_data (sensor_id, timestamp DESC);

-- Create views for sensor 
create view temperature_view
as
	select 
		timestamp
		,measurement
	from sensor_data
	where sensor_id = '5d6d5269953683001ae46ae1'
	order by timestamp;

create view pm10_view
as
	select 
		timestamp
		,measurement
	from sensor_data
	where sensor_id = '5d6d5269953683001ae46add'
	order by timestamp;

create view pm25_view
as
	select 
		timestamp
		,measurement
	from sensor_data
	where sensor_id = '5d6d5269953683001ae46ade'
	order by timestamp;

create view airPressure_view
as
	select 
		timestamp
		,measurement
	from sensor_data
	where sensor_id = '607fe08260979a001bd13188'
	order by timestamp;

create view illuminance_view
as
	select 
		timestamp
		,measurement
	from sensor_data
	where sensor_id = '5e7f6fecf7afec001bf5b1a3'
	order by timestamp;

create view humidity_view
as
	select 
		timestamp
		,measurement
	from sensor_data
	where sensor_id = '5d6d5269953683001ae46ae0'
	order by timestamp;

-- Create hourly aggregated materialized views

create materialized view temperature_hourly_avg
as
	select 
		date_trunc('hour', timestamp) as timestamp
		,avg(measurement) as measurement
	from temperature_view
	group by date_trunc('hour', timestamp)
	order by date_trunc('hour', timestamp);
	
create materialized view pm10_hourly_avg
as
	select 
		date_trunc('hour', timestamp) as timestamp
		,avg(measurement) as measurement
	from pm10_view
	group by date_trunc('hour', timestamp)
	order by date_trunc('hour', timestamp);
	
create materialized view pm25_hourly_avg
as
	select 
		date_trunc('hour', timestamp) as timestamp
		,avg(measurement) as measurement
	from pm25_view
	group by date_trunc('hour', timestamp)
	order by date_trunc('hour', timestamp);
	
create materialized view airPressure_hourly_avg
as
	select 
		date_trunc('hour', timestamp) as timestamp
		,avg(measurement) as measurement
	from airPressure_view
	group by date_trunc('hour', timestamp)
	order by date_trunc('hour', timestamp);
	
create materialized view illuminance_hourly_avg
as
	select 
		date_trunc('hour', timestamp) as timestamp
		,avg(measurement) as measurement
	from illuminance_view
	group by date_trunc('hour', timestamp)
	order by date_trunc('hour', timestamp);
	
create materialized view humidity_hourly_avg
as
	select 
		date_trunc('hour', timestamp) as timestamp
		,avg(measurement) as measurement
	from humidity_view
	group by date_trunc('hour', timestamp)
	order by date_trunc('hour', timestamp);
	
-- Create daily aggregated materialized views

create materialized view temperature_daily_avg
as
	select 
		date_trunc('day', timestamp) as timestamp
		,avg(measurement) as measurement
	from temperature_view
	group by date_trunc('day', timestamp)
	order by date_trunc('day', timestamp);
	
create materialized view pm10_daily_avg
as
	select 
		date_trunc('day', timestamp) as timestamp
		,avg(measurement) as measurement
	from pm10_view
	group by date_trunc('day', timestamp)
	order by date_trunc('day', timestamp);
	
create materialized view pm25_daily_avg
as
	select 
		date_trunc('day', timestamp) as timestamp
		,avg(measurement) as measurement
	from pm25_view
	group by date_trunc('day', timestamp)
	order by date_trunc('day', timestamp);
	
create materialized view airPressure_daily_avg
as
	select 
		date_trunc('day', timestamp) as timestamp
		,avg(measurement) as measurement
	from airPressure_view
	group by date_trunc('day', timestamp)
	order by date_trunc('day', timestamp);
	
create materialized view illuminance_daily_avg
as
	select 
		date_trunc('day', timestamp) as timestamp
		,avg(measurement) as measurement
	from illuminance_view
	group by date_trunc('day', timestamp)
	order by date_trunc('day', timestamp);
	
create materialized view humidity_daily_avg
as
	select 
		date_trunc('day', timestamp) as timestamp
		,avg(measurement) as measurement
	from humidity_view
	group by date_trunc('day', timestamp)
	order by date_trunc('day', timestamp);