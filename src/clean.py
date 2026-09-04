
import pandas as pd


# ============================================================
# CONFIGURACIÓN
# ============================================================

# GENDERIZE_URL = "https://api.genderize.io"

# # Cantidad de nombres enviados por petición
# BATCH_SIZE = 10

# # Tiempo de espera entre lotes
# WAIT_BETWEEN_BATCHES = 1

# # Cantidad de reintentos cuando aparece HTTP 429
# MAX_RETRIES = 5


# # ============================================================
# # CONSULTAR GENDERIZE POR LOTES
# # ============================================================

# def get_gender_estimates(names):
#     """
#     Consulta Genderize por lotes.

#     Parameters
#     ----------
#     names : list
#         Lista de nombres únicos.

#     Returns
#     -------
#     dict
#         Diccionario nombre -> género.
#     """

#     gender_map = {}

#     # --------------------------------------------------------
#     # Dividir nombres en lotes
#     # --------------------------------------------------------

#     batches = [
#         names[i:i + BATCH_SIZE]
#         for i in range(0, len(names), BATCH_SIZE)
#     ]

#     print(
#         f"\nNombres únicos: {len(names)}"
#     )

#     print(
#         f"Lotes a procesar: {len(batches)}"
#     )

#     # --------------------------------------------------------
#     # Procesar cada lote
#     # --------------------------------------------------------

#     for batch_number, batch in enumerate(batches, 1):

#         retries = 0

#         while retries < MAX_RETRIES:

#             try:

#                 # ------------------------------------------------
#                 # Crear parámetros
#                 #
#                 # Genderize recibe varios name:
#                 #
#                 # ?name=MARIA&name=JOHN&name=BERNIE
#                 # ------------------------------------------------

#                 params = [
#                     ("name", name)
#                     for name in batch
#                 ]

#                 response = requests.get(
#                     GENDERIZE_URL,
#                     params=params,
#                     timeout=10
#                 )

#                 # ------------------------------------------------
#                 # Éxito
#                 # ------------------------------------------------

#                 if response.status_code == 200:

#                     data = response.json()

#                     # La API puede devolver:
#                     # - una lista si se enviaron varios nombres
#                     # - un objeto si se envió uno solo

#                     if isinstance(data, dict):
#                         data = [data]

#                     for result in data:

#                         name = result.get("name")
#                         gender = result.get("gender")
#                         probability = result.get(
#                             "probability",
#                             0
#                         )

#                         # ----------------------------------------
#                         # Solo aceptar estimaciones >= 0.8
#                         # ----------------------------------------

#                         if (
#                             gender is not None
#                             and probability >= 0.8
#                         ):
#                             gender_map[name.upper()] = (
#                                 gender.upper()
#                             )
#                         else:
#                             gender_map[name.upper()] = "UNKNOWN"

#                     print(
#                         f"✓ Lote {batch_number}/"
#                         f"{len(batches)} procesado "
#                         f"({len(batch)} nombres)"
#                     )

#                     break

#                 # ------------------------------------------------
#                 # Error 429: demasiadas solicitudes
#                 # ------------------------------------------------

#                 elif response.status_code == 429:

#                     retries += 1

#                     # Espera progresiva:
#                     #
#                     # 2, 4, 8, 16, 32 segundos
#                     #
#                     wait_time = 2 ** retries

#                     print(
#                         f"⚠ HTTP 429 en lote "
#                         f"{batch_number}. "
#                         f"Esperando {wait_time} segundos..."
#                     )

#                     time.sleep(wait_time)

#                 # ------------------------------------------------
#                 # Otro error HTTP
#                 # ------------------------------------------------

#                 else:

#                     print(
#                         f"⚠ Error HTTP "
#                         f"{response.status_code} "
#                         f"en lote {batch_number}"
#                     )

#                     # Los nombres del lote quedan UNKNOWN

#                     for name in batch:

#                         gender_map[name.upper()] = "UNKNOWN"

#                     break

#             except requests.RequestException as e:

#                 retries += 1

#                 wait_time = 2 ** retries

#                 print(
#                     f"⚠ Error de conexión: {e}"
#                 )

#                 print(
#                     f"Reintentando en "
#                     f"{wait_time} segundos..."
#                 )

#                 time.sleep(wait_time)

#         # --------------------------------------------------------
#         # Si agotó los reintentos
#         # --------------------------------------------------------

#         if retries >= MAX_RETRIES:

#             print(
#                 f"✗ Se agotaron los reintentos "
#                 f"para el lote {batch_number}"
#             )

#             for name in batch:

#                 gender_map[name.upper()] = "UNKNOWN"

#         # --------------------------------------------------------
#         # Esperar antes del siguiente lote
#         # --------------------------------------------------------

#         time.sleep(WAIT_BETWEEN_BATCHES)

#     return gender_map


# # ============================================================
# # CLEAN
# # ============================================================

def clean(df):
    """
    Limpia y transforma el DataFrame de candidatos.
    """
    df_candidates = df.copy()


    # ========================================================
    # 2. RENOMBRAR COLUMNAS
    # ========================================================

    df_candidates = df_candidates.rename(
        columns={
            "First Name": "first_name",
            "Last Name": "last_name",
            "Email": "email",
            "Application Date": "application_date",
            "Country": "country",
            "YOE": "years_of_experience",
            "Seniority": "seniority",
            "Technology": "technology",
            "Code Challenge Score":
                "code_challenge_score",
            "Technical Interview Score":
                "technical_interview_score"
        }
    )


    df_candidates["first_name"] = (
        df_candidates["first_name"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    df_candidates["last_name"] = (
        df_candidates["last_name"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    df_candidates["application_date"] = (
        pd.to_datetime(
            df_candidates["application_date"],
            errors="coerce"
        )
    )

 
    df_candidates["country"] = (
        df_candidates["country"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    df_candidates["seniority"] = (
        df_candidates["seniority"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    df_candidates["technology"] = (
        df_candidates["technology"]
        .astype("string")
        .str.strip()
        .str.upper()
    )


    # ========================================================
    # 6. CONVERTIR SCORES A NUMÉRICOS
    # ========================================================

    df_candidates["code_challenge_score"] = (
        pd.to_numeric(
            df_candidates["code_challenge_score"],
            errors="coerce"
        )
    )

    df_candidates["technical_interview_score"] = (
        pd.to_numeric(
            df_candidates["technical_interview_score"],
            errors="coerce"
        )
    )

    df_candidates["candidate_id"] = (
        df_candidates["first_name"] + "_" +
        df_candidates["last_name"] + "_" +
        df_candidates["email"].astype("string").str.strip().str.lower()
    )

    df_candidates["years_of_experience"] = (
        pd.to_numeric(
            df_candidates["years_of_experience"],
            errors="coerce"
        )
    )


    # ========================================================
    # 7. CALCULAR IS_HIRED
    # ========================================================

    df_candidates["is_hired"] = (
        (
            df_candidates["code_challenge_score"] >= 7
        )
        &
        (
            df_candidates["technical_interview_score"] >= 7
        )
    ).astype(int)


    # ========================================================
    # 8. ESTIMAR GÉNERO POR LOTES
    # ========================================================

    # print("\n" + "=" * 60)
    # print("ESTIMACIÓN DE GÉNERO")
    # print("=" * 60)

    # print(
    #     f"Total de candidatos: "
    #     f"{len(df_candidates)}"
    # )

    # --------------------------------------------------------
    # Obtener nombres únicos
    # --------------------------------------------------------

    # unique_names = (
    #     df_candidates["first_name"]
    #     .dropna()
    #     .unique()
    #     .tolist()
    # )

    # --------------------------------------------------------
    # Consultar Genderize por lotes
    # --------------------------------------------------------

    # gender_map = get_gender_estimates(
    #     unique_names
    # )

    # --------------------------------------------------------
    # Asignar género a cada candidato
    # --------------------------------------------------------

    # ========================================================
    # 9. RESUMEN
    # ========================================================

    # print("\n" + "=" * 60)
    # print("RESULTADO DE ESTIMACIÓN DE GÉNERO")
    # print("=" * 60)

    # ========================================================
    # 10. RETORNAR DATAFRAME
    # ========================================================

    return df_candidates

