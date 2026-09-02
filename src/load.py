from pathlib import Path
import pandas as pd
import mysql.connector
from mysql.connector import Error

PROJECT_ROOT = Path(__file__).parent.parent
CSV_OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "integrated_candidates.csv"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "port":3307,
    "password": "1234",
    "database": "candidates"
}



def save_to_csv(df, output_path=CSV_OUTPUT_PATH):
    """Guarda el DataFrame transformado en un archivo CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"✓ Archivo CSV guardado en: {output_path}")
    return df


def get_db_connection():
    """Obtiene la conexión a la base de datos."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"✗ Error de conexión: {e}")
        return None


def load_dim_dates(cursor, candidates_df):
    """Carga la dimensión de fechas a partir de las fechas de aplicación."""
    print("\nCargando dim_dates...")
    
    # Obtener fechas únicas
    unique_dates = pd.to_datetime(candidates_df["application_date"]).dt.normalize().unique()
    unique_dates = sorted(unique_dates)
    
    print(f"  DEBUG: Total de fechas únicas encontradas: {len(unique_dates)}")
    
    records = []
    for date in unique_dates:
        ts = pd.Timestamp(date)
        date_id = int(ts.strftime("%Y%m%d"))
        year = ts.year
        month_number = ts.month
        day_of_week = ts.dayofweek
        records.append((date_id, year, month_number, day_of_week))
    
    print(f"  DEBUG: Total de registros preparados: {len(records)}")
    
    try:
        # Usar executemany para insertar múltiples registros de una vez
        cursor.executemany(
            "INSERT IGNORE INTO dim_dates (date_id, year, month_number, day_of_week) VALUES (%s, %s, %s, %s)",
            records
        )
        print(f"✓ {cursor.rowcount} registros insertados en dim_dates")
    except Error as e:
        print(f"✗ Error al cargar dim_dates: {e}")


def load_dim_candidate(cursor, candidates_df):
    """Carga la dimensión de candidatos."""
    print("\nCargando dim_candidate...")
    
    # Obtener candidatos únicos
    candidates_unique = candidates_df[['first_name', 'last_name', 'email', 'gender_estimate']].drop_duplicates()
    
    records = []
    for _, row in candidates_unique.iterrows():
        records.append((row['first_name'], row['last_name'], row['email'], row['gender_estimate']))
    
    try:
        for record in records:
            cursor.execute(
                "INSERT IGNORE INTO dim_candidate (first_name, last_name, email, gender_estimated) VALUES (%s, %s, %s, %s)",
                record
            )
        print(f"✓ {len(records)} registros insertados en dim_candidate")
    except Error as e:
        print(f"✗ Error al cargar dim_candidate: {e}")


def load_dim_country(cursor, candidates_df):
    """Carga la dimensión de país."""
    print("\nCargando dim_country...")
    
    unique_countries = candidates_df["country"].unique()
    
    try:
        for country in unique_countries:
            cursor.execute(
                "INSERT IGNORE INTO dim_country (country_name) VALUES (%s)",
                (country,)
            )
        print(f"✓ {len(unique_countries)} registros insertados en dim_country")
    except Error as e:
        print(f"✗ Error al cargar dim_country: {e}")


def load_dim_seniority(cursor, candidates_df):
    """Carga la dimensión de seniority."""
    print("\nCargando dim_seniority...")
    
    unique_seniorities = candidates_df["seniority"].unique()
    
    try:
        for seniority in unique_seniorities:
            cursor.execute(
                "INSERT IGNORE INTO dim_seniority (seniority_name) VALUES (%s)",
                (seniority,)
            )
        print(f"✓ {len(unique_seniorities)} registros insertados en dim_seniority")
    except Error as e:
        print(f"✗ Error al cargar dim_seniority: {e}")


def load_dim_technology(cursor, candidates_df):
    """Carga la dimensión de tecnología."""
    print("\nCargando dim_technology...")
    
    unique_technologies = candidates_df["technology"].unique()
    
    try:
        for technology in unique_technologies:
            cursor.execute(
                "INSERT IGNORE INTO dim_technology (technology_name) VALUES (%s)",
                (technology,)
            )
        print(f"✓ {len(unique_technologies)} registros insertados en dim_technology")
    except Error as e:
        print(f"✗ Error al cargar dim_technology: {e}")


def load_fact_application(cursor, candidates_df):
    """Carga la tabla de hechos fact_application."""
    print("\nCargando fact_application...")
    
    records = []
    for _, row in candidates_df.iterrows():
        # Convertir application_date a date_id
        date_id = int(pd.Timestamp(row['application_date']).strftime("%Y%m%d"))
        
        # Obtener las claves de las dimensiones
        cursor.execute("SELECT candidate_key FROM dim_candidate WHERE email = %s", (row['email'],))
        candidate_key_result = cursor.fetchone()
        candidate_key = candidate_key_result[0] if candidate_key_result else None
        
        cursor.execute("SELECT country_key FROM dim_country WHERE country_name = %s", (row['country'],))
        country_key_result = cursor.fetchone()
        country_key = country_key_result[0] if country_key_result else None
        
        cursor.execute("SELECT seniority_key FROM dim_seniority WHERE seniority_name = %s", (row['seniority'],))
        seniority_key_result = cursor.fetchone()
        seniority_key = seniority_key_result[0] if seniority_key_result else None
        
        cursor.execute("SELECT technology_key FROM dim_technology WHERE technology_name = %s", (row['technology'],))
        technology_key_result = cursor.fetchone()
        technology_key = technology_key_result[0] if technology_key_result else None
        
        # Calcular score_gap
        score_gap = row['code_challenge_score'] - row['technical_interview_score']
        
        records.append((
            date_id,
            candidate_key,
            country_key,
            seniority_key,
            technology_key,
            row['code_challenge_score'],
            row['technical_interview_score'],
            row['years_of_experience'],
            row['is_hired'],
            score_gap,
            1,  # cantidad_candidatos (1 por cada fila)
            row['is_hired'],  # cantidad_contrataciones (es_hired)
            (row['is_hired'] * 100)  # proporcion_contratacion
        ))
    
    try:
        for record in records:
            cursor.execute(
                """INSERT INTO fact_application 
                   (date_id, candidate_key, country_key, seniority_key, technology_key, 
                    code_challenge_score, technical_interview_score, yoe, is_hired, score_gap,
                    cantidad_candidatos, cantidad_contrataciones, proporcion_contratacion) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                record
            )
        print(f"✓ {len(records)} registros insertados en fact_application")
    except Error as e:
        print(f"✗ Error al cargar fact_application: {e}")


def load_all_dimensions_facts(candidates_df):
    """Carga todas las dimensiones y la tabla de hechos."""
    connection = get_db_connection()
    
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        print("=" * 60)
        print("CARGANDO DATOS AL MODELO DIMENSIONAL")
        print("=" * 60)
        
        # Cargar dimensiones
        load_dim_dates(cursor, candidates_df)
        load_dim_country(cursor, candidates_df)
        load_dim_seniority(cursor, candidates_df)
        load_dim_technology(cursor, candidates_df)
        load_dim_candidate(cursor, candidates_df)
        
        # Confirmar cambios después de cargar dimensiones
        connection.commit()
        
        # Cargar fact table
        load_fact_application(cursor, candidates_df)
        
        # Confirmar todos los cambios
        connection.commit()
        
        print("\n" + "=" * 60)
        print("✓ Carga de datos completada exitosamente")
        print("=" * 60)
        return True
        
    except Error as e:
        print(f"✗ Error durante la carga: {e}")
        connection.rollback()
        return False
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

