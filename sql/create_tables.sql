-- Tabla de dimensión de fechas

CREATE TABLE IF NOT EXISTS dim_dates (
    date_id INT PRIMARY KEY,
    year INT NOT NULL,
    month_number INT NOT NULL,
    day_of_week INT NOT NULL
);

-- Tabla de dimensión de candidatos
CREATE TABLE IF NOT EXISTS dim_candidate (
    candidate_key INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    gender_estimated VARCHAR(50)
);

-- Tabla de dimensión de país
CREATE TABLE IF NOT EXISTS dim_country (
    country_key INT PRIMARY KEY AUTO_INCREMENT,
    country_name VARCHAR(100) NOT NULL UNIQUE
);

-- Tabla de dimensión de seniority
CREATE TABLE IF NOT EXISTS dim_seniority (
    seniority_key INT PRIMARY KEY AUTO_INCREMENT,
    seniority_name VARCHAR(100) NOT NULL UNIQUE
);

-- Tabla de dimensión de tecnología
CREATE TABLE IF NOT EXISTS dim_technology (
    technology_key INT PRIMARY KEY AUTO_INCREMENT,
    technology_name VARCHAR(100) NOT NULL UNIQUE
);

-- Tabla de hechos (Fact Table)
CREATE TABLE IF NOT EXISTS fact_application (
    application_key INT PRIMARY KEY AUTO_INCREMENT,
    date_id INT NOT NULL,
    candidate_key INT NOT NULL,
    country_key INT NOT NULL,
    seniority_key INT NOT NULL,
    technology_key INT NOT NULL,
    code_challenge_score DECIMAL(3, 1),
    technical_interview_score DECIMAL(3, 1),
    yoe INT,
    is_hired INT,
    score_gap DECIMAL(3, 1),
    cantidad_candidatos INT,
    cantidad_contrataciones INT,
    proporcion_contratacion DECIMAL(5, 2),
    FOREIGN KEY (date_id) REFERENCES dim_dates(date_id),
    FOREIGN KEY (candidate_key) REFERENCES dim_candidate(candidate_key),
    FOREIGN KEY (country_key) REFERENCES dim_country(country_key),
    FOREIGN KEY (seniority_key) REFERENCES dim_seniority(seniority_key),
    FOREIGN KEY (technology_key) REFERENCES dim_technology(technology_key)
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX idx_fact_date ON fact_application(date_id);
CREATE INDEX idx_fact_candidate ON fact_application(candidate_key);
CREATE INDEX idx_fact_country ON fact_application(country_key);
CREATE INDEX idx_fact_seniority ON fact_application(seniority_key);
CREATE INDEX idx_fact_technology ON fact_application(technology_key);
