import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


required_variables = {
    "DB_HOST": DB_HOST,
    "DB_PORT": DB_PORT,
    "DB_NAME": DB_NAME,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
}


missing_variables = [
    name
    for name, value in required_variables.items()
    if not value
]


if missing_variables:
    raise RuntimeError(
        "Faltan variables de entorno: "
        + ", ".join(missing_variables)
    )


DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


def test_connection():
    """
    Comprueba la conexión con PostgreSQL.
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        print("Conexión a PostgreSQL exitosa.")

        return True

    except Exception as error:
        print(
            f"Error conectando a PostgreSQL: {error}"
        )

        return False


def ensure_upsert_indexes() -> None:
    """Crea las claves únicas necesarias para los UPSERTs."""

    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS "
                "uq_weather_city_datetime "
                "ON weather_hourly (city, datetime)"
            )
        )
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS "
                "uq_weather_summary_city "
                "ON weather_summary (city)"
            )
        )