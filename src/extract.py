import json
from datetime import datetime
from pathlib import Path

import requests


API_URL = "https://api.open-meteo.com/v1/forecast"

CONFIG_FILE = Path("config/cities.json")


def load_cities():
    """
    Carga las ciudades y coordenadas desde el archivo de configuración.
    """

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de configuración: {CONFIG_FILE}"
        )

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def fetch_weather(city_name, latitude, longitude):
    """
    Obtiene los datos meteorológicos de una ciudad desde Open-Meteo.
    """

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "wind_speed_10m"
        ),
        "forecast_days": 7,
        "timezone": "America/Bogota",
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.Timeout:
        print(f"Error: timeout al consultar {city_name}")
        return None

    except requests.exceptions.ConnectionError:
        print(f"Error: no se pudo conectar con la API para {city_name}")
        return None

    except requests.exceptions.HTTPError as error:
        print(
            f"Error HTTP al consultar {city_name}: {error}"
        )
        return None

    except requests.exceptions.RequestException as error:
        print(
            f"Error de conexión con {city_name}: {error}"
        )
        return None


def extract_weather_data():
    """
    Extrae los datos de todas las ciudades configuradas.
    """

    cities = load_cities()

    extracted_data = []

    for city_name, coordinates in cities.items():

        print(f"Extrayendo datos de {city_name}...")

        weather_data = fetch_weather(
            city_name,
            coordinates["latitude"],
            coordinates["longitude"],
        )

        if weather_data is None:
            print(f"Se omitirá {city_name}.\n")
            continue

        extracted_data.append(
            {
                "city": city_name,
                "latitude": coordinates["latitude"],
                "longitude": coordinates["longitude"],
                "data": weather_data,
            }
        )

    if not extracted_data:
        raise RuntimeError(
            "No se pudieron obtener datos de ninguna ciudad."
        )

    return extracted_data


def save_raw_data(data):
    """
    Guarda la respuesta original de la API en formato JSON.
    """

    raw_directory = Path("data/raw")
    raw_directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_file = (
        raw_directory
        / f"weather_{timestamp}.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4,
        )

    print(
        f"\nDatos RAW guardados en: {output_file}"
    )

    return output_file


if __name__ == "__main__":
    data = extract_weather_data()
    save_raw_data(data)