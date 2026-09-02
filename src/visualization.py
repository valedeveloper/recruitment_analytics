import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
from mysql.connector import Error
from pathlib import Path

# Configuración
PROJECT_ROOT = Path(__file__).parent.parent
VISUALIZATIONS_PATH = PROJECT_ROOT / "results" / "visualizations"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "port": 3307,
    "password": "1234",
    "database": "candidates"
}

# Crear carpeta de visualizaciones si no existe
VISUALIZATIONS_PATH.mkdir(parents=True, exist_ok=True)

# Configurar estilo
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)


def get_db_connection():
    """Obtiene la conexión a la base de datos."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"✗ Error de conexión: {e}")
        return None


def execute_query(query):
    """Ejecuta una query y retorna un DataFrame."""
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        df = pd.read_sql(query, connection)
        return df
    except Error as e:
        print(f"✗ Error al ejecutar query: {e}")
        return None
    finally:
        if connection.is_connected():
            connection.close()


# ============================================================
# QUERY 1: Evolución de contrataciones por tiempo
# ============================================================
def visualizar_evolucion_tiempo():
    """Query 1: Evolución de contrataciones por año, mes y día."""
    print("\n[1/6] Generando gráfica: Evolución de contrataciones por tiempo...")
    
    query = """
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
    """
    
    df = execute_query(query)
    if df is None or df.empty:
        print("✗ No hay datos para visualizar")
        return
    
    # Crear subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Evolución de Contrataciones por Tiempo', fontsize=16, fontweight='bold')
    
    # 1. Contrataciones por año
    df_year = df.groupby('year')[['total_aplicaciones', 'total_contratados']].sum()
    df_year.plot(kind='bar', ax=axes[0, 0], color=['#3498db', '#2ecc71'])
    axes[0, 0].set_title('Total de Aplicaciones y Contrataciones por Año', fontweight='bold')
    axes[0, 0].set_xlabel('Año')
    axes[0, 0].set_ylabel('Cantidad')
    axes[0, 0].legend(['Total Aplicaciones', 'Total Contratados'])
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # 2. Proporción de contratación por año
    df_prop_year = df.groupby('year')['proporcion_contratacion_pct'].mean()
    axes[0, 1].plot(df_prop_year.index, df_prop_year.values, marker='o', linewidth=2, markersize=8, color='#e74c3c')
    axes[0, 1].set_title('Proporción Promedio de Contratación por Año', fontweight='bold')
    axes[0, 1].set_xlabel('Año')
    axes[0, 1].set_ylabel('Proporción (%)')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Contrataciones por mes
    df_month = df.groupby('month_number')[['total_aplicaciones', 'total_contratados']].sum()
    df_month.plot(kind='bar', ax=axes[1, 0], color=['#3498db', '#2ecc71'])
    axes[1, 0].set_title('Total de Aplicaciones y Contrataciones por Mes', fontweight='bold')
    axes[1, 0].set_xlabel('Mes')
    axes[1, 0].set_ylabel('Cantidad')
    axes[1, 0].legend(['Total Aplicaciones', 'Total Contratados'])
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # 4. Contrataciones por día de la semana
    dias_semana = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
    df_day = df.groupby('day_of_week')[['total_aplicaciones', 'total_contratados']].sum()
    df_day.index = df_day.index.map(dias_semana)
    df_day.plot(kind='bar', ax=axes[1, 1], color=['#3498db', '#2ecc71'])
    axes[1, 1].set_title('Total de Aplicaciones y Contrataciones por Día de la Semana', fontweight='bold')
    axes[1, 1].set_xlabel('Día de la Semana')
    axes[1, 1].set_ylabel('Cantidad')
    axes[1, 1].legend(['Total Aplicaciones', 'Total Contratados'])
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_PATH / '01_evolucion_tiempo.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfica guardada: 01_evolucion_tiempo.png")
    plt.close()


# ============================================================
# QUERY 2: Comparación de contrataciones entre tecnologías
# ============================================================
def visualizar_tecnologias():
    """Query 2: Comparación de tecnologías."""
    print("\n[2/6] Generando gráfica: Comparación por tecnologías...")
    
    query = """
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
    """
    
    df = execute_query(query)
    if df is None or df.empty:
        print("✗ No hay datos para visualizar")
        return
    
    # Crear subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Análisis de Contrataciones por Tecnología', fontsize=16, fontweight='bold')
    
    # 1. Cantidad de contratados por tecnología
    df_sorted = df.sort_values('cantidad_contratados', ascending=True)
    axes[0, 0].barh(df_sorted['technology_name'], df_sorted['cantidad_contratados'], color='#3498db')
    axes[0, 0].set_title('Cantidad de Contratados por Tecnología', fontweight='bold')
    axes[0, 0].set_xlabel('Cantidad Contratados')
    
    # 2. Proporción de contratación por tecnología
    df_sorted2 = df.sort_values('proporcion_contratacion_pct', ascending=True)
    axes[0, 1].barh(df_sorted2['technology_name'], df_sorted2['proporcion_contratacion_pct'], color='#2ecc71')
    axes[0, 1].set_title('Proporción de Contratación por Tecnología (%)', fontweight='bold')
    axes[0, 1].set_xlabel('Proporción (%)')
    
    # 3. Desempeño promedio en evaluaciones
    df_plot = df.sort_values('cantidad_contratados', ascending=False).head(10)
    x = range(len(df_plot))
    axes[1, 0].plot(x, df_plot['promedio_code_challenge'], marker='o', label='Code Challenge', linewidth=2)
    axes[1, 0].plot(x, df_plot['promedio_technical_interview'], marker='s', label='Technical Interview', linewidth=2)
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(df_plot['technology_name'], rotation=45, ha='right')
    axes[1, 0].set_title('Desempeño Promedio en Evaluaciones (Top 10)', fontweight='bold')
    axes[1, 0].set_ylabel('Score Promedio')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Relación entre candidatos aplicados y contratados
    df_sorted3 = df.sort_values('total_candidatos', ascending=False).head(10)
    x_pos = range(len(df_sorted3))
    width = 0.35
    axes[1, 1].bar([i - width/2 for i in x_pos], df_sorted3['total_candidatos'], width, label='Total Candidatos', color='#3498db')
    axes[1, 1].bar([i + width/2 for i in x_pos], df_sorted3['cantidad_contratados'], width, label='Contratados', color='#2ecc71')
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels(df_sorted3['technology_name'], rotation=45, ha='right')
    axes[1, 1].set_title('Candidatos Aplicados vs Contratados (Top 10)', fontweight='bold')
    axes[1, 1].set_ylabel('Cantidad')
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_PATH / '02_tecnologias.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfica guardada: 02_tecnologias.png")
    plt.close()


# ============================================================
# QUERY 3: Análisis por seniority y experiencia
# ============================================================
def visualizar_seniority_experiencia():
    """Query 3: Análisis por seniority y años de experiencia."""
    print("\n[3/6] Generando gráfica: Análisis por seniority y experiencia...")
    
    query = """
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
    """
    
    df = execute_query(query)
    if df is None or df.empty:
        print("✗ No hay datos para visualizar")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Análisis de Contrataciones por Seniority y Años de Experiencia', fontsize=16, fontweight='bold')
    
    # 1. Contratados por seniority
    df_sen = df.groupby('seniority_name')[['cantidad_contratados']].sum().sort_values('cantidad_contratados', ascending=False)
    axes[0, 0].bar(df_sen.index, df_sen['cantidad_contratados'], color='#3498db')
    axes[0, 0].set_title('Total Contratados por Nivel de Seniority', fontweight='bold')
    axes[0, 0].set_ylabel('Cantidad Contratados')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # 2. Proporción de contratación por seniority
    df_prop_sen = df.groupby('seniority_name')['proporcion_contratacion_pct'].mean().sort_values(ascending=False)
    axes[0, 1].bar(df_prop_sen.index, df_prop_sen.values, color='#2ecc71')
    axes[0, 1].set_title('Proporción Promedio de Contratación por Seniority', fontweight='bold')
    axes[0, 1].set_ylabel('Proporción (%)')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # 3. Contratados por seniority y experiencia (heatmap)
    pivot_table = df.pivot_table(values='cantidad_contratados', index='seniority_name', columns='anos_experiencia', fill_value=0)
    sns.heatmap(pivot_table, annot=True, fmt='g', cmap='YlGn', ax=axes[1, 0], cbar_kws={'label': 'Cantidad Contratados'})
    axes[1, 0].set_title('Heatmap: Contratados por Seniority y Años de Experiencia', fontweight='bold')
    axes[1, 0].set_ylabel('Nivel de Seniority')
    axes[1, 0].set_xlabel('Años de Experiencia')
    
    # 4. Proporción de contratación por seniority y experiencia
    pivot_prop = df.pivot_table(values='proporcion_contratacion_pct', index='seniority_name', columns='anos_experiencia', fill_value=0)
    sns.heatmap(pivot_prop, annot=True, fmt='.1f', cmap='RdYlGn', ax=axes[1, 1], cbar_kws={'label': 'Proporción (%)'})
    axes[1, 1].set_title('Heatmap: Proporción de Contratación por Seniority y Experiencia', fontweight='bold')
    axes[1, 1].set_ylabel('Nivel de Seniority')
    axes[1, 1].set_xlabel('Años de Experiencia')
    
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_PATH / '03_seniority_experiencia.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfica guardada: 03_seniority_experiencia.png")
    plt.close()


# ============================================================
# QUERY 4: Desempeño técnico por país y experiencia
# ============================================================
def visualizar_pais_experiencia():
    """Query 4: Desempeño técnico por país y experiencia."""
    print("\n[4/6] Generando gráfica: Desempeño por país y experiencia...")
    
    query = """
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
    """
    
    df = execute_query(query)
    if df is None or df.empty:
        print("✗ No hay datos para visualizar")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Desempeño Técnico por País y Años de Experiencia', fontsize=16, fontweight='bold')
    
    # 1. Top 10 países por cantidad de contratados
    df_top_paises = df.groupby('country_name')[['cantidad_contratados']].sum().sort_values('cantidad_contratados', ascending=False).head(10)
    axes[0, 0].barh(df_top_paises.index, df_top_paises['cantidad_contratados'], color='#3498db')
    axes[0, 0].set_title('Top 10 Países por Cantidad de Contratados', fontweight='bold')
    axes[0, 0].set_xlabel('Cantidad Contratados')
    
    # 2. Top 10 países por proporción de contratación
    df_prop_paises = df.groupby('country_name')['proporcion_contratacion_pct'].mean().sort_values(ascending=False).head(10)
    axes[0, 1].barh(df_prop_paises.index, df_prop_paises.values, color='#2ecc71')
    axes[0, 1].set_title('Top 10 Países por Proporción de Contratación', fontweight='bold')
    axes[0, 1].set_xlabel('Proporción (%)')
    
    # 3. Desempeño promedio por experiencia (todas las regiones)
    df_exp = df.groupby('anos_experiencia')[['promedio_code_challenge', 'promedio_technical_interview']].mean()
    axes[1, 0].plot(df_exp.index, df_exp['promedio_code_challenge'], marker='o', label='Code Challenge', linewidth=2)
    axes[1, 0].plot(df_exp.index, df_exp['promedio_technical_interview'], marker='s', label='Technical Interview', linewidth=2)
    axes[1, 0].set_title('Desempeño Promedio según Años de Experiencia', fontweight='bold')
    axes[1, 0].set_xlabel('Años de Experiencia')
    axes[1, 0].set_ylabel('Score Promedio')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Proporción de contratación por experiencia
    df_prop_exp = df.groupby('anos_experiencia')['proporcion_contratacion_pct'].mean()
    axes[1, 1].plot(df_prop_exp.index, df_prop_exp.values, marker='o', linewidth=2, markersize=8, color='#e74c3c')
    axes[1, 1].set_title('Proporción de Contratación según Años de Experiencia', fontweight='bold')
    axes[1, 1].set_xlabel('Años de Experiencia')
    axes[1, 1].set_ylabel('Proporción (%)')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_PATH / '04_pais_experiencia.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfica guardada: 04_pais_experiencia.png")
    plt.close()


# ============================================================
# QUERY 5: Diferencias Code Challenge vs Technical Interview
# ============================================================
def visualizar_diferencia_evaluaciones():
    """Query 5: Diferencias entre evaluaciones."""
    print("\n[5/6] Generando gráfica: Diferencia entre evaluaciones...")
    
    query = """
    SELECT 
        ROUND(AVG(f.code_challenge_score), 2) AS promedio_code_challenge,
        ROUND(AVG(f.technical_interview_score), 2) AS promedio_technical_interview,
        ROUND(AVG(f.score_gap), 2) AS promedio_diferencia,
        COUNT(*) AS total_candidatos,
        SUM(CASE WHEN f.score_gap > 0 THEN 1 ELSE 0 END) AS candidatos_mejor_en_code,
        SUM(CASE WHEN f.score_gap < 0 THEN 1 ELSE 0 END) AS candidatos_mejor_en_interview,
        SUM(CASE WHEN f.score_gap = 0 THEN 1 ELSE 0 END) AS candidatos_igual_en_ambas
    FROM fact_application AS f;
    """
    
    df = execute_query(query)
    if df is None or df.empty:
        print("✗ No hay datos para visualizar")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Análisis de Diferencias entre Code Challenge y Technical Interview', fontsize=16, fontweight='bold')
    
    # 1. Comparación de promedios
    evaluaciones = ['Code Challenge', 'Technical Interview']
    promedios = [df['promedio_code_challenge'].iloc[0], df['promedio_technical_interview'].iloc[0]]
    axes[0, 0].bar(evaluaciones, promedios, color=['#3498db', '#2ecc71'])
    axes[0, 0].set_title('Promedio de Scores por Evaluación', fontweight='bold')
    axes[0, 0].set_ylabel('Score Promedio')
    for i, v in enumerate(promedios):
        axes[0, 0].text(i, v + 0.1, f'{v:.2f}', ha='center', fontweight='bold')
    
    # 2. Distribución de candidatos por desempeño relativo
    categorias = ['Mejor en Code\nChallenge', 'Mejor en Technical\nInterview', 'Igual en Ambas']
    valores = [
        df['candidatos_mejor_en_code'].iloc[0],
        df['candidatos_mejor_en_interview'].iloc[0],
        df['candidatos_igual_en_ambas'].iloc[0]
    ]
    colors = ['#3498db', '#e74c3c', '#f39c12']
    axes[0, 1].pie(valores, labels=categorias, autopct='%1.1f%%', colors=colors, startangle=90)
    axes[0, 1].set_title('Distribución de Candidatos por Desempeño Relativo', fontweight='bold')
    
    # 3. Diferencia promedio (score_gap)
    axes[1, 0].text(0.5, 0.5, f'Score Gap Promedio:\n{df["promedio_diferencia"].iloc[0]:.2f}', 
                   ha='center', va='center', fontsize=20, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.8))
    axes[1, 0].axis('off')
    axes[1, 0].set_title('Score Gap Promedio (Code Challenge - Technical Interview)', fontweight='bold')
    
    # 4. Resumen de métricas
    axes[1, 1].axis('off')
    metrics_text = f"""
MÉTRICAS GLOBALES

Total de Candidatos: {int(df['total_candidatos'].iloc[0]):,}

Promedio Code Challenge: {df['promedio_code_challenge'].iloc[0]:.2f}
Promedio Technical Interview: {df['promedio_technical_interview'].iloc[0]:.2f}
Diferencia Promedio: {df['promedio_diferencia'].iloc[0]:.2f}

Mejor en Code Challenge: {int(df['candidatos_mejor_en_code'].iloc[0]):,} ({int(df['candidatos_mejor_en_code'].iloc[0])/int(df['total_candidatos'].iloc[0])*100:.1f}%)
Mejor en Technical Interview: {int(df['candidatos_mejor_en_interview'].iloc[0]):,} ({int(df['candidatos_mejor_en_interview'].iloc[0])/int(df['total_candidatos'].iloc[0])*100:.1f}%)
Igual en Ambas: {int(df['candidatos_igual_en_ambas'].iloc[0]):,} ({int(df['candidatos_igual_en_ambas'].iloc[0])/int(df['total_candidatos'].iloc[0])*100:.1f}%)
    """
    axes[1, 1].text(0.1, 0.5, metrics_text, fontsize=11, verticalalignment='center', 
                   family='monospace', bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_PATH / '05_diferencia_evaluaciones.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfica guardada: 05_diferencia_evaluaciones.png")
    plt.close()


# ============================================================
# QUERY 6: Tendencias por género estimado
# ============================================================
def visualizar_genero():
    """Query 6: Tendencias por género estimado."""
    print("\n[6/6] Generando gráfica: Tendencias por género...")
    
    query = """
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
    """
    
    df = execute_query(query)
    if df is None or df.empty:
        print("✗ No hay datos para visualizar")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Análisis de Contrataciones por Género Estimado', fontsize=16, fontweight='bold')
    
    # 1. Total de candidatos por género
    axes[0, 0].pie(df['total_candidatos'], labels=df['genero_estimado'], autopct='%1.1f%%',
                  colors=['#3498db', '#e74c3c', '#f39c12', '#95a5a6'])
    axes[0, 0].set_title('Distribución de Candidatos por Género', fontweight='bold')
    
    # 2. Cantidad de contratados por género
    axes[0, 1].bar(df['genero_estimado'], df['cantidad_contratados'], color=['#3498db', '#e74c3c', '#f39c12', '#95a5a6'][:len(df)])
    axes[0, 1].set_title('Cantidad de Contratados por Género', fontweight='bold')
    axes[0, 1].set_ylabel('Cantidad Contratados')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # 3. Proporción de contratación por género
    axes[1, 0].bar(df['genero_estimado'], df['proporcion_contratacion_pct'], color=['#3498db', '#e74c3c', '#f39c12', '#95a5a6'][:len(df)])
    axes[1, 0].set_title('Proporción de Contratación por Género (%)', fontweight='bold')
    axes[1, 0].set_ylabel('Proporción (%)')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # 4. Desempeño y experiencia por género
    ax4 = axes[1, 1]
    x = range(len(df))
    ax4_twin = ax4.twinx()
    
    bar1 = ax4.bar([i - 0.2 for i in x], df['promedio_code_challenge'], 0.4, label='Code Challenge', color='#3498db')
    bar2 = ax4.bar([i + 0.2 for i in x], df['promedio_technical_interview'], 0.4, label='Technical Interview', color='#2ecc71')
    line = ax4_twin.plot(x, df['promedio_anos_experiencia'], 'o-', label='Años de Experiencia', color='#e74c3c', linewidth=2, markersize=8)
    
    ax4.set_xticks(x)
    ax4.set_xticklabels(df['genero_estimado'], rotation=45, ha='right')
    ax4.set_ylabel('Score Promedio', color='black')
    ax4_twin.set_ylabel('Años de Experiencia', color='#e74c3c')
    ax4.set_title('Desempeño y Experiencia por Género', fontweight='bold')
    ax4.legend(loc='upper left')
    ax4_twin.legend(loc='upper right')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(VISUALIZATIONS_PATH / '06_genero.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfica guardada: 06_genero.png")
    plt.close()


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def main():
    """Ejecuta todas las visualizaciones."""
    print("=" * 70)
    print("GENERACIÓN DE GRÁFICAS ANALÍTICAS")
    print("=" * 70)
    
    visualizar_evolucion_tiempo()
    visualizar_tecnologias()
    visualizar_seniority_experiencia()
    visualizar_pais_experiencia()
    visualizar_diferencia_evaluaciones()
    visualizar_genero()
    
    print("\n" + "=" * 70)
    print("✓ Todas las gráficas han sido generadas exitosamente")
    print(f"✓ Ubicación: {VISUALIZATIONS_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    main()
