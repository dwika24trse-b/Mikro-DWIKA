-- Skema Database MySQL untuk MoniQuarium (Monitoring Aquarium Pintar)
-- Anda dapat mengeksekusi script ini di phpMyAdmin, MySQL Workbench, atau terminal MySQL.

CREATE DATABASE IF NOT EXISTS aquarium_db;
USE aquarium_db;

CREATE TABLE IF NOT EXISTS sensor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    temperature FLOAT NOT NULL,    -- Suhu air (°C)
    ph FLOAT NOT NULL,             -- Tingkat pH air (0 - 14)
    turbidity FLOAT NOT NULL,      -- Tingkat kejernihan air (%)
    water_level FLOAT NOT NULL,    -- Tingkat ketinggian air (%)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Indeks opsional untuk mempercepat pencarian data berdasarkan waktu
CREATE INDEX idx_created_at ON sensor_data(created_at);
