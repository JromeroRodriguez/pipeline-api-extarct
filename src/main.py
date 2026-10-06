from src.extract import (
    extract_weather_data,
    save_raw_data,
)

from src.transform import transform

from src.validate import validate_weather_data

from src.analyze import generate_city_summary

from src.load import (
    save_processed_data,
    save_summary_data,
    save_to_postgresql,
)

from src.database import test_connection


def main() -> None:
    """
    Ejecuta el pipeline completo.
    """

    # -----------------------------------------
    # DATABASE CONNECTION
    # -----------------------------------------
    if not test_connection():
        raise RuntimeError(
            "No se puede ejecutar el pipeline "
            "sin conexión a PostgreSQL."
        )

    print("=" * 60)
    print("INICIANDO WEATHER DATA PIPELINE")
    print("=" * 60)

    # -----------------------------------------
    # EXTRACT
    # -----------------------------------------
    print("\n[1/5] EXTRACT")

    raw_data = extract_weather_data()

    raw_file = save_raw_data(
        raw_data
    )

    # -----------------------------------------
    # TRANSFORM
    # -----------------------------------------
    print("\n[2/5] TRANSFORM")

    df = transform()

    print(
        f"Registros horarios: {len(df)}"
    )

    # -----------------------------------------
    # VALIDATE
    # -----------------------------------------
    print("\n[3/5] VALIDATE")

    validate_weather_data(df)

    # -----------------------------------------
    # ANALYZE
    # -----------------------------------------
    print("\n[4/5] ANALYZE")

    summary_df = generate_city_summary(
        df
    )

    print(
        f"Ciudades analizadas: "
        f"{len(summary_df)}"
    )

    # -----------------------------------------
    # LOAD
    # -----------------------------------------
    print("\n[5/5] LOAD")

    processed_file = save_processed_data(
        df
    )

    summary_file = save_summary_data(
        summary_df
    )

    save_to_postgresql(
        df,
        summary_df,
    )

    # -----------------------------------------
    # FINAL
    # -----------------------------------------
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETADO")
    print("=" * 60)

    print("\nRAW:")
    print(f"  {raw_file}")

    print("\nDatos procesados:")
    print(f"  {processed_file}")

    print("\nResumen:")
    print(f"  {summary_file}")

    print("\nResumen por ciudad:")
    print(
        summary_df.to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()