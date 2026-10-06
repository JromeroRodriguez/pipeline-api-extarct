import pandas as pd


REQUIRED_COLUMNS = [
    "city",
    "latitude",
    "longitude",
    "datetime",
    "temperature_c",
    "humidity_pct",
    "precipitation_mm",
    "wind_speed_kmh",
]


def validate_required_columns(df: pd.DataFrame) -> list[str]:
    """
    Verifica que todas las columnas requeridas existan.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    return missing_columns


def validate_nulls(df: pd.DataFrame) -> list[str]:
    """
    Verifica valores nulos en columnas esenciales.
    """

    columns_to_check = [
        "city",
        "datetime",
        "temperature_c",
        "humidity_pct",
        "precipitation_mm",
        "wind_speed_kmh",
    ]

    errors = []

    for column in columns_to_check:
        null_count = df[column].isna().sum()

        if null_count > 0:
            errors.append(
                f"{column}: {null_count} valores nulos"
            )

    return errors


def validate_numeric_columns(df: pd.DataFrame) -> list[str]:
    """
    Verifica que las columnas numéricas tengan tipos numéricos.
    """

    numeric_columns = [
        "latitude",
        "longitude",
        "temperature_c",
        "humidity_pct",
        "precipitation_mm",
        "wind_speed_kmh",
    ]

    errors = []

    for column in numeric_columns:
        if not pd.api.types.is_numeric_dtype(df[column]):
            errors.append(
                f"{column}: contiene datos no numéricos"
            )

    return errors


def validate_ranges(df: pd.DataFrame) -> list[str]:
    """
    Verifica que los valores estén dentro de rangos válidos.
    """

    errors = []

    invalid_humidity = (
        (df["humidity_pct"] < 0)
        | (df["humidity_pct"] > 100)
    ).sum()

    if invalid_humidity > 0:
        errors.append(
            f"humidity_pct: {invalid_humidity} valores fuera de 0-100"
        )

    invalid_precipitation = (
        df["precipitation_mm"] < 0
    ).sum()

    if invalid_precipitation > 0:
        errors.append(
            f"precipitation_mm: {invalid_precipitation} valores negativos"
        )

    invalid_wind = (
        df["wind_speed_kmh"] < 0
    ).sum()

    if invalid_wind > 0:
        errors.append(
            f"wind_speed_kmh: {invalid_wind} valores negativos"
        )

    invalid_latitude = (
        (df["latitude"] < -90)
        | (df["latitude"] > 90)
    ).sum()

    if invalid_latitude > 0:
        errors.append(
            f"latitude: {invalid_latitude} valores fuera de -90 a 90"
        )

    invalid_longitude = (
        (df["longitude"] < -180)
        | (df["longitude"] > 180)
    ).sum()

    if invalid_longitude > 0:
        errors.append(
            f"longitude: {invalid_longitude} valores fuera de -180 a 180"
        )

    return errors


def validate_duplicates(df: pd.DataFrame) -> list[str]:
    """
    Verifica registros duplicados por ciudad y fecha/hora.
    """

    duplicated = df.duplicated(
        subset=["city", "datetime"]
    ).sum()

    if duplicated > 0:
        return [
            f"Se encontraron {duplicated} registros duplicados"
        ]

    return []


def validate_weather_data(df: pd.DataFrame) -> bool:
    """
    Ejecuta todas las validaciones del DataFrame.

    Retorna True si los datos son válidos.
    Lanza ValueError si encuentra errores.
    """

    errors = []

    # DataFrame vacío
    if df.empty:
        errors.append(
            "El DataFrame está vacío"
        )
        raise ValueError(
            "Validación fallida:\n- "
            + "\n- ".join(errors)
        )

    # Columnas requeridas
    missing_columns = validate_required_columns(df)

    if missing_columns:
        errors.append(
            "Faltan columnas: "
            + ", ".join(missing_columns)
        )

        raise ValueError(
            "Validación fallida:\n- "
            + "\n- ".join(errors)
        )

    # Valores nulos
    errors.extend(
        validate_nulls(df)
    )

    # Tipos numéricos
    errors.extend(
        validate_numeric_columns(df)
    )

    # Rangos
    errors.extend(
        validate_ranges(df)
    )

    # Duplicados
    errors.extend(
        validate_duplicates(df)
    )

    if errors:
        print("\n VALIDACIÓN FALLIDA")

        for error in errors:
            print(f"   - {error}")

        raise ValueError(
            "Los datos no cumplen las reglas de calidad."
        )

    print("\n VALIDACIÓN EXITOSA")

    print(f"   Registros validados: {len(df)}")
    print(f"   Ciudades: {df['city'].nunique()}")
    print(f"   Columnas: {len(df.columns)}")

    return True