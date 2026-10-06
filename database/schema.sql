CREATE TABLE IF NOT EXISTS weather_hourly (
    id BIGSERIAL PRIMARY KEY,

    city VARCHAR(100) NOT NULL,

    latitude NUMERIC(9, 6) NOT NULL,

    longitude NUMERIC(9, 6) NOT NULL,

    datetime TIMESTAMP NOT NULL,

    temperature_c NUMERIC(5, 2),

    humidity_pct NUMERIC(5, 2),

    precipitation_mm NUMERIC(8, 2),

    wind_speed_kmh NUMERIC(8, 2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_weather_city_datetime
        UNIQUE (city, datetime),

    CONSTRAINT chk_humidity
        CHECK (
            humidity_pct >= 0
            AND humidity_pct <= 100
        ),

    CONSTRAINT chk_precipitation
        CHECK (
            precipitation_mm >= 0
        ),

    CONSTRAINT chk_wind_speed
        CHECK (
            wind_speed_kmh >= 0
        ),

    CONSTRAINT chk_latitude
        CHECK (
            latitude >= -90
            AND latitude <= 90
        ),

    CONSTRAINT chk_longitude
        CHECK (
            longitude >= -180
            AND longitude <= 180
        )
);


CREATE TABLE IF NOT EXISTS weather_summary (
    id BIGSERIAL PRIMARY KEY,

    city VARCHAR(100) NOT NULL UNIQUE,

    temperature_min NUMERIC(5, 2),

    temperature_max NUMERIC(5, 2),

    temperature_avg NUMERIC(5, 2),

    humidity_avg NUMERIC(5, 2),

    precipitation_total NUMERIC(10, 2),

    wind_speed_avg NUMERIC(8, 2),

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_summary_humidity
        CHECK (
            humidity_avg >= 0
            AND humidity_avg <= 100
        ),

    CONSTRAINT chk_summary_precipitation
        CHECK (
            precipitation_total >= 0
        ),

    CONSTRAINT chk_summary_wind
        CHECK (
            wind_speed_avg >= 0
        )
);


CREATE INDEX IF NOT EXISTS idx_weather_hourly_city
    ON weather_hourly(city);


CREATE INDEX IF NOT EXISTS idx_weather_hourly_datetime
    ON weather_hourly(datetime);


CREATE INDEX IF NOT EXISTS idx_weather_hourly_city_datetime
    ON weather_hourly(city, datetime);