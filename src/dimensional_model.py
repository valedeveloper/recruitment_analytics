from pathlib import Path
import psycopg2
from psycopg2 import Error
from config import DB_CONFIG, DB_SERVER_CONFIG

# Configuración de paths y base de datos
PROJECT_ROOT = Path(__file__).parent.parent
SQL_FILE_PATH = PROJECT_ROOT / "sql" / "create_tables.sql"

DB_NAME = "candidates"


def read_sql_file(file_path):
    """Lee el archivo SQL y retorna una lista de comandos SQL."""
    with open(file_path, 'r', encoding='utf-8') as file:
        sql_content = file.read()
    
    # Dividir por puntos y coma para separar múltiples comandos SQL
    sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
    return sql_commands


def create_database_if_not_exists():
    """Crea la base de datos si no existe."""
    try:
        config = DB_SERVER_CONFIG.copy()
        connection = psycopg2.connect(**config, database="postgres")
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        if cursor.fetchone() is None:
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
        print(f"✓ Base de datos '{DB_NAME}' lista para usar\n")
        cursor.close()
        connection.close()
    
    except Error as e:
        print(f"✗ Error al crear la base de datos: {e}")
        raise


def create_dimensional_tables():
    """Crea las tablas dimensionales y de hechos en la base de datos."""
    try:
        # Crear la base de datos primero
        create_database_if_not_exists()
        
        # Establecer conexión a la base de datos
        config = DB_CONFIG.copy()
        config["database"] = DB_NAME
        connection = psycopg2.connect(**config)
        print("✓ Conexión exitosa a la base de datos 'candidates'")
        cursor = connection.cursor()

        # Leer los comandos SQL del archivo
        sql_commands = read_sql_file(SQL_FILE_PATH)
        print(f"✓ Archivo SQL leído: {len(sql_commands)} comandos encontrados\n")

        # Ejecutar cada comando SQL
        for i, command in enumerate(sql_commands, 1):
            try:
                cursor.execute(command)
                connection.commit()
                print(f"✓ Comando {i} ejecutado correctamente")
            except Error as e:
                print(f"✗ Error en comando {i}: {e}")
                connection.rollback()

        print("\n✓ Todas las tablas han sido creadas exitosamente")

        # Verificar las tablas creadas
        cursor.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public' ORDER BY tablename")
        tables = cursor.fetchall()
        print(f"\nTablas en la base de datos:")
        for table in tables:
            print(f"  - {table[0]}")
    
    except Error as e:
        print(f"✗ Error de conexión a PostgreSQL: {e}")
    
    finally:
        # Cerrar la conexión
        if 'connection' in locals() and not connection.closed:
            cursor.close()
            connection.close()
            print("\n✓ Conexión a la base de datos cerrada")


if __name__ == "__main__":
    print("=" * 50)
    print("CREACIÓN DE MODELO DIMENSIONAL")
    print("=" * 50 + "\n")
    create_dimensional_tables()
