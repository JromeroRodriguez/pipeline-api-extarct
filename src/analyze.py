import pandas as pd


def generate_city_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un resumen estadístico por ciudad.
    """

    summary = (
        df.groupby("city")
        .agg(
            temperature_min=("temperature_c", "min"),
            temperature_max=("temperature_c", "max"),
            temperature_avg=("temperature_c", "mean"),
            humidity_avg=("humidity_pct", "mean"),
            precipitation_total=("precipitation_mm", "sum"),
            wind_speed_avg=("wind_speed_kmh", "mean"),
        )
        .reset_index()
    )

    # Redondear valores numéricos
    numeric_columns = [
        "temperature_min",
        "temperature_max",
        "temperature_avg",
        "humidity_avg",
        "precipitation_total",
        "wind_speed_avg",
    ]

    summary[numeric_columns] = (
        summary[numeric_columns].round(2)
    )

    # Ordenar por temperatura promedio descendente
    summary = (
        summary.sort_values(
            by="temperature_avg",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    return summary