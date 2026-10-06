from pathlib import Path

import pandas as pd

from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import insert

from src.database import engine, ensure_upsert_indexes


PROCESSED_DIRECTORY = Path("data/processed")

PROCESSED_FILE = (
    PROCESSED_DIRECTORY
    / "weather_processed.csv"
)

SUMMARY_FILE = (
    PROCESSED_DIRECTORY
    / "weather_summary.csv"
)


def save_processed_data(df: pd.DataFrame) -> Path:
    """
    Guarda los datos horarios procesados en CSV.
    El archivo se sobrescribe en cada ejecución.
    """

    PROCESSED_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        PROCESSED_FILE,
        index=False,
        encoding="utf-8",
    )

    print(
        f"Datos horarios guardados en: "
        f"{PROCESSED_FILE}"
    )

    return PROCESSED_FILE


def save_summary_data(
    df_summary: pd.DataFrame,
) -> Path:
    """
    Guarda el resumen estadístico en CSV.
    El archivo se sobrescribe en cada ejecución.
    """

    PROCESSED_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    df_summary.to_csv(
        SUMMARY_FILE,
        index=False,
        encoding="utf-8",
    )

    print(
        f"Resumen por ciudad guardado en: "
        f"{SUMMARY_FILE}"
    )

    return SUMMARY_FILE


def get_weather_hourly_table() -> Table:
    """
    Obtiene la definición de weather_hourly
    desde PostgreSQL.
    """

    metadata = MetaData()

    return Table(
        "weather_hourly",
        metadata,
        autoload_with=engine,
    )


def get_weather_summary_table() -> Table:
    """
    Obtiene la definición de weather_summary
    desde PostgreSQL.
    """

    metadata = MetaData()

    return Table(
        "weather_summary",
        metadata,
        autoload_with=engine,
    )


def upsert_weather_hourly(
    df: pd.DataFrame,
) -> None:
    """
    Inserta nuevos registros horarios o actualiza
    los existentes utilizando city + datetime.
    """

    if df.empty:
        return

    columns = [
        "city",
        "latitude",
        "longitude",
        "datetime",
        "temperature_c",
        "humidity_pct",
        "precipitation_mm",
        "wind_speed_kmh",
    ]

    data = df[columns].copy()

    # Convertir NaN/NaT a None
    data = (
        data.astype(object)
        .where(pd.notna(data), None)
    )

    records = data.to_dict(
        orient="records"
    )

    table = get_weather_hourly_table()

    statement = insert(table).values(
        records
    )

    statement = statement.on_conflict_do_update(
        index_elements=[
            "city",
            "datetime",
        ],
        set_={
            "latitude": statement.excluded.latitude,
            "longitude": statement.excluded.longitude,
            "temperature_c": statement.excluded.temperature_c,
            "humidity_pct": statement.excluded.humidity_pct,
            "precipitation_mm": statement.excluded.precipitation_mm,
            "wind_speed_kmh": statement.excluded.wind_speed_kmh,
        },
    )

    with engine.begin() as connection:
        connection.execute(statement)

    print(
        f"UPSERT weather_hourly: "
        f"{len(records)} registros."
    )


def upsert_weather_summary(
    df_summary: pd.DataFrame,
) -> None:
    """
    Inserta nuevos resúmenes o actualiza
    los existentes utilizando city.
    """

    if df_summary.empty:
        return

    columns = [
        "city",
        "temperature_min",
        "temperature_max",
        "temperature_avg",
        "humidity_avg",
        "precipitation_total",
        "wind_speed_avg",
    ]

    data = df_summary[columns].copy()

    # Convertir NaN a None
    data = (
        data.astype(object)
        .where(pd.notna(data), None)
    )

    records = data.to_dict(
        orient="records"
    )

    table = get_weather_summary_table()

    statement = insert(table).values(
        records
    )

    statement = statement.on_conflict_do_update(
        index_elements=["city"],
        set_={
            "temperature_min": statement.excluded.temperature_min,
            "temperature_max": statement.excluded.temperature_max,
            "temperature_avg": statement.excluded.temperature_avg,
            "humidity_avg": statement.excluded.humidity_avg,
            "precipitation_total": statement.excluded.precipitation_total,
            "wind_speed_avg": statement.excluded.wind_speed_avg,
        },
    )

    with engine.begin() as connection:
        connection.execute(statement)

    print(
        f"UPSERT weather_summary: "
        f"{len(records)} registros."
    )


def save_to_postgresql(
    df: pd.DataFrame,
    df_summary: pd.DataFrame,
) -> None:
    """
    Carga los datos transformados y analizados
    en PostgreSQL mediante UPSERT.
    """

    ensure_upsert_indexes()

    upsert_weather_hourly(df)

    upsert_weather_summary(
        df_summary
    )

    print(
        "Datos cargados correctamente "
        "en PostgreSQL."
    )