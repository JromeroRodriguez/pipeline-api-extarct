import json
from pathlib import Path

import pandas as pd


RAW_DIRECTORY = Path("data/raw")


def get_latest_raw_file():
    """
    Obtiene el archivo RAW más reciente.
    """

    raw_files = list(
        RAW_DIRECTORY.glob("weather_*.json")
    )

    if not raw_files:
        raise FileNotFoundError(
            "No se encontraron archivos RAW en data/raw/"
        )

    return max(
        raw_files,
        key=lambda file: file.stat().st_mtime,
    )


def load_raw_data(file_path):
    """
    Carga el archivo JSON RAW.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def transform_weather_data(raw_data):
    """
    Convierte los datos RAW en un DataFrame
    limpio y estructurado.
    """

    records = []

    for city in raw_data:
        city_name = city["city"]
        latitude = city["latitude"]
        longitude = city["longitude"]

        hourly_data = city["data"]["hourly"]

        times = hourly_data["time"]
        temperatures = hourly_data["temperature_2m"]
        humidity = hourly_data[
            "relative_humidity_2m"
        ]
        precipitation = hourly_data[
            "precipitation"
        ]
        wind_speed = hourly_data[
            "wind_speed_10m"
        ]

        for i in range(len(times)):
            records.append(
                {
                    "city": city_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "datetime": times[i],
                    "temperature_c": temperatures[i],
                    "humidity_pct": humidity[i],
                    "precipitation_mm": precipitation[i],
                    "wind_speed_kmh": wind_speed[i],
                }
            )

    df = pd.DataFrame(records)

    # Convertir fecha
    df["datetime"] = pd.to_datetime(
        df["datetime"]
    )

    # Convertir valores numéricos
    numeric_columns = [
        "latitude",
        "longitude",
        "temperature_c",
        "humidity_pct",
        "precipitation_mm",
        "wind_speed_kmh",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    # Eliminar registros completamente duplicados
    df = df.drop_duplicates()

    # Eliminar registros con datos esenciales faltantes
    df = df.dropna(
        subset=[
            "city",
            "datetime",
            "temperature_c",
        ]
    )

    # Ordenar por ciudad y fecha
    df = (
        df.sort_values(
            by=["city", "datetime"]
        )
        .reset_index(drop=True)
    )

    return df


def transform():
    """
    Ejecuta el proceso completo de transformación.
    """

    raw_file = get_latest_raw_file()

    print(
        f"Procesando archivo: {raw_file}"
    )

    raw_data = load_raw_data(
        raw_file
    )

    df = transform_weather_data(
        raw_data
    )

    print(
        "\nTransformación completada."
    )

    print(
        f"Registros procesados: {len(df)}"
    )

    return df


if __name__ == "__main__":
    df = transform()

    print("\nPrimeros registros:")
    print(df.head())

    print("\nInformación del DataFrame:")
    df.info()