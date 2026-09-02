-- ============================================================
-- QUERY 1: Monitorear la evolución de contrataciones por tiempo
-- ============================================================
-- Analiza la tendencia de contrataciones por año, mes y día de la semana
SELECT 
    d.year,
    d.month_number,
    d.day_of_week,
    COUNT(*) AS total_aplicaciones,
    SUM(f.is_hired) AS total_contratados,
    ROUND(SUM(f.is_hired) / COUNT(*) * 100, 2) AS proporcion_contratacion_pct
FROM fact_application AS f
JOIN dim_dates AS d ON f.date_id = d.date_id
GROUP BY d.year, d.month_number, d.day_of_week
ORDER BY d.year, d.month_number, d.day_of_week;


-- ============================================================
-- QUERY 2: Comparación de contrataciones entre tecnologías
-- ============================================================
-- Identifica qué tecnologías tienen mayor cantidad y proporción de candidatos contratados
SELECT 
    t.technology_name,
    COUNT(*) AS total_candidatos,
    SUM(f.is_hired) AS cantidad_contratados,
    ROUND(SUM(f.is_hired) / COUNT(*) * 100, 2) AS proporcion_contratacion_pct,
    ROUND(AVG(f.code_challenge_score), 2) AS promedio_code_challenge,
    ROUND(AVG(f.technical_interview_score), 2) AS promedio_technical_interview
FROM fact_application AS f
JOIN dim_technology AS t ON f.technology_key = t.technology_key
GROUP BY t.technology_name
ORDER BY cantidad_contratados DESC;


-- ============================================================
-- QUERY 3: Análisis de contratación por seniority y años de experiencia
-- ============================================================
-- Analiza resultados de contratación según nivel de seniority y años de experiencia
SELECT 
    s.seniority_name,
    f.yoe AS anos_experiencia,
    COUNT(*) AS total_candidatos,
    SUM(f.is_hired) AS cantidad_contratados,
    ROUND(SUM(f.is_hired) / COUNT(*) * 100, 2) AS proporcion_contratacion_pct,
    ROUND(AVG(f.code_challenge_score), 2) AS promedio_code_challenge,
    ROUND(AVG(f.technical_interview_score), 2) AS promedio_technical_interview
FROM fact_application AS f
JOIN dim_seniority AS s ON f.seniority_key = s.seniority_key
GROUP BY s.seniority_name, f.yoe
ORDER BY s.seniority_name, f.yoe;


-- ============================================================
-- QUERY 4: Desempeño técnico por años de experiencia y país
-- ============================================================
-- Analiza el desempeño en evaluaciones técnicas según experiencia y país del candidato
SELECT 
    c.country_name,
    f.yoe AS anos_experiencia,
    COUNT(*) AS total_candidatos,
    ROUND(AVG(f.code_challenge_score), 2) AS promedio_code_challenge,
    ROUND(AVG(f.technical_interview_score), 2) AS promedio_technical_interview,
    SUM(f.is_hired) AS cantidad_contratados,
    ROUND(SUM(f.is_hired) / COUNT(*) * 100, 2) AS proporcion_contratacion_pct
FROM fact_application AS f
JOIN dim_country AS c ON f.country_key = c.country_key
GROUP BY c.country_name, f.yoe
ORDER BY c.country_name, f.yoe;


-- ============================================================
-- QUERY 5: Diferencias entre Code Challenge y Technical Interview
-- ============================================================
-- Identifica diferencias relevantes entre el desempeño en ambas evaluaciones
SELECT 
    ROUND(AVG(f.code_challenge_score), 2) AS promedio_code_challenge,
    ROUND(AVG(f.technical_interview_score), 2) AS promedio_technical_interview,
    ROUND(AVG(f.score_gap), 2) AS promedio_diferencia,
    COUNT(*) AS total_candidatos,
    SUM(CASE WHEN f.score_gap > 0 THEN 1 ELSE 0 END) AS candidatos_mejor_en_code,
    SUM(CASE WHEN f.score_gap < 0 THEN 1 ELSE 0 END) AS candidatos_mejor_en_interview,
    SUM(CASE WHEN f.score_gap = 0 THEN 1 ELSE 0 END) AS candidatos_igual_en_ambas
FROM fact_application AS f;


-- ============================================================
-- QUERY 6: Tendencias de contratación por género estimado
-- ============================================================
-- Analiza proporciones y tendencias de contratación según género estimado
SELECT 
    COALESCE(dc.gender_estimated, 'UNKNOWN') AS genero_estimado,
    COUNT(*) AS total_candidatos,
    SUM(f.is_hired) AS cantidad_contratados,
    ROUND(SUM(f.is_hired) / COUNT(*) * 100, 2) AS proporcion_contratacion_pct,
    ROUND(AVG(f.code_challenge_score), 2) AS promedio_code_challenge,
    ROUND(AVG(f.technical_interview_score), 2) AS promedio_technical_interview,
    ROUND(AVG(f.yoe), 2) AS promedio_anos_experiencia
FROM fact_application AS f
JOIN dim_candidate AS dc ON f.candidate_key = dc.candidate_key
GROUP BY dc.gender_estimated
ORDER BY cantidad_contratados DESC;
