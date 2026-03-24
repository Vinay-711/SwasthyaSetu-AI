-- Delta Lake: Patients table schema
-- Run in Databricks SQL Editor or as part of ETL notebook

CREATE DATABASE IF NOT EXISTS swasthya;

CREATE TABLE IF NOT EXISTS swasthya.patients (
    patient_id      STRING        NOT NULL COMMENT 'Unique 8-char alphanumeric health ID',
    name            STRING        NOT NULL,
    age             INT,
    gender          STRING,
    blood_group     STRING,
    phone           STRING,
    occupation      STRING,
    region          STRING,
    created_at      TIMESTAMP     DEFAULT current_timestamp(),
    updated_at      TIMESTAMP     DEFAULT current_timestamp()
)
USING DELTA
COMMENT 'Patient master records for SwasthyaSetu AI'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact'   = 'true'
);
