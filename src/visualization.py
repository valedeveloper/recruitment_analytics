import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2
from psycopg2 import Error
from pathlib import Path
from config import DB_CONFIG


PROJECT_ROOT = Path(__file__).parent.parent
VISUALIZATIONS_PATH = PROJECT_ROOT / "results" / "visualizations"
VISUALIZATIONS_PATH.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="colorblind")
plt.rcParams.update({
    "figure.dpi": 120,
    "axes.titleweight": "bold",
    "axes.titlesize": 12,
    "axes.labelsize": 10,
})

HIRED_COLOR = "#168aad"
APPLICATION_COLOR = "#6c757d"
RATE_COLOR = "#e76f51"
CODE_COLOR = "#457b9d"
INTERVIEW_COLOR = "#e76f51"


def get_db_connection():
    """Obtiene la conexión a la base de datos."""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Error as error:
        print(f"✗ Error de conexión: {error}")
    return None


def execute_query(query):
    """Ejecuta una query y retorna un DataFrame."""
    connection = get_db_connection()
    if not connection:
        return None

    try:
        return pd.read_sql(query, connection)
    except Error as error:
        print(f"✗ Error al ejecutar query: {error}")
        return None
    finally:
        if not connection.closed:
            connection.close()


def save_figure(figure, filename):
    """Guarda una figura con el mismo nombre usado en el README."""
    figure.savefig(VISUALIZATIONS_PATH / filename, dpi=300, bbox_inches="tight")
    plt.close(figure)
    print(f"✓ Gráfica guardada: {filename}")


def add_value_labels(axis, bars, formatter="{:,.0f}"):
    """Agrega valores legibles a barras horizontales o verticales."""
    for bar in bars:
        if bar.get_width() != 0:
            value = bar.get_width()
            axis.text(value, bar.get_y() + bar.get_height() / 2, f" {formatter.format(value)}", va="center", fontsize=8)
        else:
            value = bar.get_height()
            axis.text(bar.get_x() + bar.get_width() / 2, value, f"{formatter.format(value)}", ha="center", va="bottom", fontsize=8)


# ============================================================
# QUERY 1: Evolución de contrataciones por tiempo
# ============================================================
def visualizar_evolucion_tiempo():
    """Muestra volumen, tasa y comportamiento semanal de las contrataciones."""
    print("\n[1/5] Generando gráfica: Evolución de contrataciones por tiempo...")

    query = """
    SELECT d.date_id, d.year, d.month_number, d.day_of_week,
           COUNT(*) AS total_aplicaciones, SUM(f.is_hired) AS total_contratados
    FROM fact_application AS f
    JOIN dim_dates AS d ON f.date_id = d.date_id
    GROUP BY d.date_id, d.year, d.month_number, d.day_of_week
    ORDER BY d.date_id;
    """
    df = execute_query(query)
    if df is None or df.empty:
        print("✗ No hay datos para visualizar")
        return

    df_year = df.groupby("year", as_index=False)[["total_aplicaciones", "total_contratados"]].sum()
    df_year["tasa_contratacion_pct"] = df_year["total_contratados"] / df_year["total_aplicaciones"] * 100
    df_month = df.groupby("month_number", as_index=False)[["total_aplicaciones", "total_contratados"]].sum()
    df_day = df.groupby("day_of_week", as_index=False)[["total_aplicaciones", "total_contratados"]].sum()
    df_day["tasa_contratacion_pct"] = df_day["total_contratados"] / df_day["total_aplicaciones"] * 100

    month_names = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    day_names = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]
    figure, axes = plt.subplots(2, 2, figsize=(16, 10))
    figure.suptitle("R1 | ¿Cómo evolucionan las contrataciones en el tiempo?", fontsize=16, fontweight="bold")

    axes[0, 0].plot(df_year["year"], df_year["total_aplicaciones"], marker="o", color=APPLICATION_COLOR, label="Aplicaciones")
    axes[0, 0].plot(df_year["year"], df_year["total_contratados"], marker="o", color=HIRED_COLOR, label="Contratados")
    axes[0, 0].set_title("Volumen anual de aplicaciones y contrataciones")
    axes[0, 0].set_ylabel("Candidatos")
    axes[0, 0].legend(frameon=False)

    axes[0, 1].plot(df_year["year"], df_year["tasa_contratacion_pct"], marker="o", color=RATE_COLOR, linewidth=2)
    axes[0, 1].set_title("La tasa de contratación anual")
    axes[0, 1].set_ylabel("Contratados / aplicaciones (%)")
    axes[0, 1].set_ylim(bottom=0)
    for _, row in df_year.iterrows():
        axes[0, 1].annotate(f"{row['tasa_contratacion_pct']:.1f}%", (row["year"], row["tasa_contratacion_pct"]), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8)

    axes[1, 0].bar(df_month["month_number"], df_month["total_aplicaciones"], color=APPLICATION_COLOR, label="Aplicaciones")
    axes[1, 0].bar(df_month["month_number"], df_month["total_contratados"], color=HIRED_COLOR, label="Contratados")
    axes[1, 0].set_title("¿En qué meses se concentra el volumen?")
    axes[1, 0].set_xlabel("Mes")
    axes[1, 0].set_ylabel("Candidatos")
    axes[1, 0].set_xticks(range(1, 13), month_names)
    axes[1, 0].legend(frameon=False)

    bars = axes[1, 1].bar(df_day["day_of_week"], df_day["tasa_contratacion_pct"], color=RATE_COLOR)
    axes[1, 1].set_title("¿Qué día tiene mayor tasa de contratación?")
    axes[1, 1].set_xlabel("Día de la semana")
    axes[1, 1].set_ylabel("Contratados / aplicaciones (%)")
    axes[1, 1].set_xticks(range(7), day_names)
    axes[1, 1].set_ylim(0, max(df_day["tasa_contratacion_pct"].max() * 1.18, 1))
    add_value_labels(axes[1, 1], bars, "{:.1f}%")

    figure.tight_layout(rect=(0, 0, 1, 0.95))
    save_figure(figure, "01_evolucion_tiempo.png")


# ============================================================
# QUERY 2: Comparación de contrataciones entre tecnologías
# ============================================================
def visualizar_tecnologias():
    """Ordena tecnologías por volumen, tasa y desempeño promedio."""
    print("\n[2/5] Generando gráfica: Comparación por tecnologías...")

    query = """
    SELECT t.technology_name, COUNT(*) AS total_candidatos,
           SUM(f.is_hired) AS cantidad_contratados,
           AVG(f.code_challenge_score) AS promedio_code_challenge,
           AVG(f.technical_interview_score) AS promedio_technical_interview
    FROM fact_application AS f
    JOIN dim_technology AS t ON f.technology_key = t.technology_key
    GROUP BY t.technology_name;
    """
    df = execute_query(query)
    if df is None or df.empty:
        print("✗ No hay datos para visualizar")
        return

    df["proporcion_contratacion_pct"] = df["cantidad_contratados"] / df["total_candidatos"] * 100
    by_hires = df.sort_values("cantidad_contratados").tail(15)
    by_rate = df.sort_values("proporcion_contratacion_pct").tail(15)
    by_score = df.sort_values("total_candidatos", ascending=False).head(15).sort_values("promedio_technical_interview")

    figure, axes = plt.subplots(1, 3, figsize=(19, 9))
    figure.suptitle("R2 | ¿Qué tecnologías producen más y mejores contrataciones?", fontsize=16, fontweight="bold")

    axes[0].barh(by_hires["technology_name"], by_hires["total_candidatos"], color=APPLICATION_COLOR, label="Aplicaciones")
    axes[0].barh(by_hires["technology_name"], by_hires["cantidad_contratados"], color=HIRED_COLOR, label="Contratados")
    axes[0].set_title("Top 15 por cantidad de contratados")
    axes[0].set_xlabel("Candidatos")
    axes[0].legend(frameon=False, loc="lower right")

    bars = axes[1].barh(by_rate["technology_name"], by_rate["proporcion_contratacion_pct"], color=RATE_COLOR)
    axes[1].set_title("Top 15 por tasa de contratación")
    axes[1].set_xlabel("Contratados / aplicaciones (%)")
    axes[1].set_xlim(0, max(by_rate["proporcion_contratacion_pct"].max() * 1.2, 1))
    add_value_labels(axes[1], bars, "{:.1f}%")

    y_positions = range(len(by_score))
    axes[2].scatter(by_score["promedio_code_challenge"], y_positions, color=CODE_COLOR, s=55, label="Code Challenge", zorder=3)
    axes[2].scatter(by_score["promedio_technical_interview"], y_positions, color=INTERVIEW_COLOR, s=55, label="Technical Interview", zorder=3)
    for position, (_, row) in enumerate(by_score.iterrows()):
        axes[2].plot([row["promedio_code_challenge"], row["promedio_technical_interview"]], [position, position], color="#adb5bd", linewidth=1)
    axes[2].set_yticks(list(y_positions), by_score["technology_name"])
    axes[2].set_title("Promedio de evaluaciones\n(15 tecnologías con más aplicaciones)")
    axes[2].set_xlabel("Puntaje promedio (0 a 10)")
    axes[2].set_xlim(0, 10)
    axes[2].legend(frameon=False, loc="lower right")

    figure.tight_layout(rect=(0, 0, 1, 0.95))
    save_figure(figure, "02_tecnologias.png")


# ============================================================
# QUERY 3: Análisis por seniority y experiencia
# ============================================================
def visualizar_seniority_experiencia():
    """Compara resultados de contratación por seniority y años de experiencia."""
    print("\n[3/5] Generando gráfica: Análisis por seniority y años de experiencia...")

    query = """
    SELECT s.seniority_name, f.yoe AS anos_experiencia, COUNT(*) AS total_candidatos,
           SUM(f.is_hired) AS cantidad_contratados,
           AVG(f.code_challenge_score) AS promedio_code_challenge,
           AVG(f.technical_interview_score) AS promedio_technical_interview
    FROM fact_application AS f
    JOIN dim_seniority AS s ON f.seniority_key = s.seniority_key
    GROUP BY s.seniority_name, f.yoe;
    """
    df = execute_query(query)
    if df is None or df.empty:
        print("✗ No hay datos para visualizar")
        return

    df["proporcion_contratacion_pct"] = df["cantidad_contratados"] / df["total_candidatos"] * 100
    seniority = df.groupby("seniority_name", as_index=False)[["total_candidatos", "cantidad_contratados"]].sum()
    seniority["proporcion_contratacion_pct"] = seniority["cantidad_contratados"] / seniority["total_candidatos"] * 100
    experience = df.groupby("anos_experiencia", as_index=False)[["total_candidatos", "cantidad_contratados"]].sum()
    experience["proporcion_contratacion_pct"] = experience["cantidad_contratados"] / experience["total_candidatos"] * 100
    scores = df.groupby("seniority_name", as_index=False)[["promedio_code_challenge", "promedio_technical_interview"]].mean().sort_values("promedio_technical_interview")

    figure, axes = plt.subplots(2, 2, figsize=(16, 11))
    figure.suptitle("R3 | ¿Qué perfiles, por seniority y experiencia, se contratan más?", fontsize=16, fontweight="bold")

    seniority_sorted = seniority.sort_values("cantidad_contratados")
    axes[0, 0].barh(seniority_sorted["seniority_name"], seniority_sorted["total_candidatos"], color=APPLICATION_COLOR, label="Aplicaciones")
    axes[0, 0].barh(seniority_sorted["seniority_name"], seniority_sorted["cantidad_contratados"], color=HIRED_COLOR, label="Contratados")
    axes[0, 0].set_title("Volumen de contratación por seniority")
    axes[0, 0].set_xlabel("Candidatos")
    axes[0, 0].legend(frameon=False)

    axes[0, 1].plot(experience["anos_experiencia"], experience["proporcion_contratacion_pct"], color=RATE_COLOR, marker="o", linewidth=2)
    axes[0, 1].set_title("Tasa de contratación según experiencia")
    axes[0, 1].set_xlabel("Años de experiencia")
    axes[0, 1].set_ylabel("Contratados / aplicaciones (%)")
    axes[0, 1].set_ylim(bottom=0)

    axes[1, 0].plot(experience["anos_experiencia"], experience["total_candidatos"], color=APPLICATION_COLOR, marker="o", label="Aplicaciones")
    axes[1, 0].plot(experience["anos_experiencia"], experience["cantidad_contratados"], color=HIRED_COLOR, marker="o", label="Contratados")
    axes[1, 0].set_title("Aplicaciones y contratados por años de experiencia")
    axes[1, 0].set_xlabel("Años de experiencia")
    axes[1, 0].set_ylabel("Candidatos")
    axes[1, 0].legend(frameon=False)

    y_positions = range(len(scores))
    axes[1, 1].scatter(scores["promedio_code_challenge"], y_positions, color=CODE_COLOR, s=55, label="Code Challenge")
    axes[1, 1].scatter(scores["promedio_technical_interview"], y_positions, color=INTERVIEW_COLOR, s=55, label="Technical Interview")
    for position, (_, row) in enumerate(scores.iterrows()):
        axes[1, 1].plot([row["promedio_code_challenge"], row["promedio_technical_interview"]], [position, position], color="#adb5bd", linewidth=1)
    axes[1, 1].set_yticks(list(y_positions), scores["seniority_name"])
    axes[1, 1].set_title("Desempeño técnico promedio por seniority")
    axes[1, 1].set_xlabel("Puntaje promedio (0 a 10)")
    axes[1, 1].set_xlim(0, 10)
    axes[1, 1].legend(frameon=False)

    figure.tight_layout(rect=(0, 0, 1, 0.95))
    save_figure(figure, "03_seniority_experiencia.png")


# ============================================================
# QUERY 4: Desempeño técnico por país y experiencia
# ============================================================
def visualizar_pais_experiencia():
    """Muestra desempeño y contratación por experiencia y países con mayor volumen."""
    print("\n[4/5] Generando gráfica: Desempeño por país y experiencia...")

    query = """
    SELECT c.country_name, f.yoe AS anos_experiencia, COUNT(*) AS total_candidatos,
           AVG(f.code_challenge_score) AS promedio_code_challenge,
           AVG(f.technical_interview_score) AS promedio_technical_interview,
           SUM(f.is_hired) AS cantidad_contratados
    FROM fact_application AS f
    JOIN dim_country AS c ON f.country_key = c.country_key
    GROUP BY c.country_name, f.yoe;
    """
    df = execute_query(query)
    if df is None or df.empty:
        print("✗ No hay datos para visualizar")
        return

    df["proporcion_contratacion_pct"] = df["cantidad_contratados"] / df["total_candidatos"] * 100
    df["code_score_total"] = df["promedio_code_challenge"] * df["total_candidatos"]
    df["interview_score_total"] = df["promedio_technical_interview"] * df["total_candidatos"]
    country = df.groupby("country_name", as_index=False)[[
        "total_candidatos", "cantidad_contratados", "code_score_total", "interview_score_total"
    ]].sum()
    country["promedio_code_challenge"] = country["code_score_total"] / country["total_candidatos"]
    country["promedio_technical_interview"] = country["interview_score_total"] / country["total_candidatos"]
    country["proporcion_contratacion_pct"] = country["cantidad_contratados"] / country["total_candidatos"] * 100
    top_countries = country.nlargest(12, "total_candidatos")["country_name"].tolist()
    top = country[country["country_name"].isin(top_countries)]
    experience = df.groupby("anos_experiencia", as_index=False)[[
        "total_candidatos", "cantidad_contratados", "code_score_total", "interview_score_total"
    ]].sum()
    experience["promedio_code_challenge"] = experience["code_score_total"] / experience["total_candidatos"]
    experience["promedio_technical_interview"] = experience["interview_score_total"] / experience["total_candidatos"]
    experience["proporcion_contratacion_pct"] = experience["cantidad_contratados"] / experience["total_candidatos"] * 100

    figure, axes = plt.subplots(2, 2, figsize=(17, 11))
    figure.suptitle("R4 | ¿Cómo cambia el desempeño técnico por país y experiencia?", fontsize=16, fontweight="bold")

    top = top.sort_values("proporcion_contratacion_pct")
    axes[0, 0].barh(top["country_name"], top["proporcion_contratacion_pct"], color=RATE_COLOR)
    axes[0, 0].set_title("Tasa de contratación\n(12 países con más aplicaciones)")
    axes[0, 0].set_xlabel("Contratados / aplicaciones (%)")

    top_scores = top.sort_values("promedio_technical_interview")
    y_positions = range(len(top_scores))
    axes[0, 1].scatter(top_scores["promedio_code_challenge"], y_positions, color=CODE_COLOR, s=50, label="Code Challenge")
    axes[0, 1].scatter(top_scores["promedio_technical_interview"], y_positions, color=INTERVIEW_COLOR, s=50, label="Technical Interview")
    axes[0, 1].set_yticks(list(y_positions), top_scores["country_name"])
    axes[0, 1].set_title("Puntajes promedio por país\n(12 países con más aplicaciones)")
    axes[0, 1].set_xlabel("Puntaje promedio (0 a 10)")
    axes[0, 1].set_xlim(0, 10)
    axes[0, 1].legend(frameon=False, loc="lower right")

    axes[1, 0].plot(experience["anos_experiencia"], experience["promedio_code_challenge"], color=CODE_COLOR, marker="o", label="Code Challenge")
    axes[1, 0].plot(experience["anos_experiencia"], experience["promedio_technical_interview"], color=INTERVIEW_COLOR, marker="o", label="Technical Interview")
    axes[1, 0].set_title("Puntajes promedio según años de experiencia")
    axes[1, 0].set_xlabel("Años de experiencia")
    axes[1, 0].set_ylabel("Puntaje promedio (0 a 10)")
    axes[1, 0].set_ylim(0, 10)
    axes[1, 0].legend(frameon=False)

    axes[1, 1].plot(experience["anos_experiencia"], experience["proporcion_contratacion_pct"], color=RATE_COLOR, marker="o", linewidth=2)
    axes[1, 1].set_title("Tasa de contratación según experiencia")
    axes[1, 1].set_xlabel("Años de experiencia")
    axes[1, 1].set_ylabel("Contratados / aplicaciones (%)")
    axes[1, 1].set_ylim(bottom=0)

    figure.tight_layout(rect=(0, 0, 1, 0.95))
    save_figure(figure, "04_pais_experiencia.png")


# ============================================================
# QUERY 5: Diferencias Code Challenge vs Technical Interview
# ============================================================
def visualizar_diferencia_evaluaciones():
    """Explica la magnitud, dirección y proporción de las brechas entre evaluaciones."""
    print("\n[5/5] Generando gráfica: Diferencia entre evaluaciones...")

    query = """
    SELECT f.code_challenge_score, f.technical_interview_score, f.score_gap, f.is_hired
    FROM fact_application AS f;
    """
    df = execute_query(query)
    if df is None or df.empty:
        print("✗ No hay datos para visualizar")
        return

    categories = pd.Series({
        "Mejor en entrevista": (df["score_gap"] > 0).sum(),
        "Igual en ambas": (df["score_gap"] == 0).sum(),
        "Mejor en code challenge": (df["score_gap"] < 0).sum(),
    }).sort_values()
    total_candidates = len(df)
    average_code = df["code_challenge_score"].mean()
    average_interview = df["technical_interview_score"].mean()
    average_gap = df["score_gap"].mean()

    figure, axes = plt.subplots(2, 2, figsize=(16, 10))
    figure.suptitle("R5 | ¿Dónde cambia el desempeño entre las dos evaluaciones?", fontsize=16, fontweight="bold")

    axes[0, 0].bar(["Code Challenge", "Technical Interview"], [average_code, average_interview], color=[CODE_COLOR, INTERVIEW_COLOR])
    axes[0, 0].set_title("Puntaje promedio por etapa")
    axes[0, 0].set_ylabel("Puntaje promedio (0 a 10)")
    axes[0, 0].set_ylim(0, 10)
    for position, value in enumerate([average_code, average_interview]):
        axes[0, 0].text(position, value + 0.2, f"{value:.2f}", ha="center", fontweight="bold")

    axes[0, 1].hist(df["score_gap"], bins=21, color="#f4a261", edgecolor="white", align="left")
    axes[0, 1].axvline(0, color="#264653", linestyle="--", linewidth=1.5)
    axes[0, 1].axvline(average_gap, color=RATE_COLOR, linestyle="-", linewidth=2, label=f"Promedio: {average_gap:.2f}")
    axes[0, 1].set_title("Distribución de la brecha de evaluación")
    axes[0, 1].set_xlabel("Score gap = entrevista - code challenge")
    axes[0, 1].set_ylabel("Candidatos")
    axes[0, 1].legend(frameon=False)

    bars = axes[1, 0].barh(categories.index, categories.values, color=[CODE_COLOR, "#adb5bd", HIRED_COLOR])
    axes[1, 0].set_title("¿En qué evaluación rinden mejor?")
    axes[1, 0].set_xlabel("Candidatos")
    add_value_labels(axes[1, 0], bars)
    for bar, value in zip(bars, categories.values):
        axes[1, 0].text(value, bar.get_y() + bar.get_height() / 2, f" ({value / total_candidates * 100:.1f}%)", va="center", fontsize=8)

    axes[1, 1].axis("off")
    metrics = (
        "KPI GLOBALES\n\n"
        f"Candidatos analizados: {total_candidates:,}\n"
        f"Promedio Code Challenge: {average_code:.2f}\n"
        f"Promedio Technical Interview: {average_interview:.2f}\n"
        f"Score gap promedio: {average_gap:.2f}\n\n"
        "Gap positivo = mejor entrevista\n"
        "Gap negativo = mejor code challenge"
    )
    axes[1, 1].text(0.08, 0.5, metrics, va="center", fontsize=13, family="monospace")

    figure.tight_layout(rect=(0, 0, 1, 0.95))
    save_figure(figure, "05_diferencia_evaluaciones.png")


def main():
    """Ejecuta las cinco visualizaciones de los requisitos R1 a R5."""
    print("=" * 70)
    print("GENERACIÓN DE GRÁFICAS ANALÍTICAS R1-R5")
    print("=" * 70)
    visualizar_evolucion_tiempo()
    visualizar_tecnologias()
    visualizar_seniority_experiencia()
    visualizar_pais_experiencia()
    visualizar_diferencia_evaluaciones()
    print("\n" + "=" * 70)
    print("✓ Todas las gráficas han sido generadas exitosamente")
    print(f"✓ Ubicación: {VISUALIZATIONS_PATH}")
    print("=" * 70)


if __name__ == "__main__":
    main()
