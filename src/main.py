from pathlib import Path
import pandas as pd
from clean import clean
from extract import extract_file_to_csv
from load import save_to_csv, load_all_dimensions_facts
from dimensional_model import create_dimensional_tables
from visualization import main as generate_visualizations


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = "data/raw/candidates.csv"

# Define la ruta del archivo asegurando que exista la carpeta
CSV_PATH_CLEANED = BASE_DIR / "data" / "processed" / "integrated_candidates.csv"

def main():
    print("=" * 70)
    print("ETL PIPELINE - MODELO DIMENSIONAL")
    print("=" * 70)
    
    # STEP 1: Creación de tablas dimensionales
    print("\n[1/4] CREANDO MODELO DIMENSIONAL...")
    print("-" * 70)
    create_dimensional_tables()
    
    # STEP 2: Extracción
    print("\n[2/4] EXTRACCIÓN DE DATOS...")
    print("-" * 70)
    df_candidates = extract_file_to_csv(CSV_PATH)
    print(f"✓ Extraídos {len(df_candidates)} registros")
    
    # STEP 3: Limpieza
    print("\n[3/4] LIMPIEZA Y TRANSFORMACIÓN DE DATOS...")
    print("-" * 70)
    df_candidates_cleaned = clean(df_candidates)
    print(f"✓ Limpieza completada. {len(df_candidates_cleaned)} registros listos")

    # STEP 4: Carga a CSV integrado
    print("\n[4/4] GUARDANDO DATOS INTEGRADOS Y CARGANDO AL DATA WAREHOUSE...")
    print("-" * 70)
    df_candidates_cleaned = save_to_csv(df_candidates_cleaned)
    
    # STEP 5: Carga a las dimensiones y fact table
    print("\nCargando datos al modelo dimensional...")
    load_all_dimensions_facts(df_candidates_cleaned)

    # STEP 6: Generación de visualizaciones
    print("\nGenerando visualizaciones...")
    generate_visualizations()

if __name__ == "__main__":
    main()