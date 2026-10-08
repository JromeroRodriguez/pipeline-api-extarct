# Weather Data Pipeline

Pipeline ETL que consulta el pronostico horario de Open-Meteo para las ciudades configuradas, valida y analiza los datos, y los guarda en archivos CSV y PostgreSQL.

## Funcionalidades

- Extrae hasta 7 dias de pronostico horario por ciudad.
- Conserva cada respuesta original como JSON.
- Transforma y valida los datos meteorologicos con pandas.
- Calcula estadisticas por ciudad: temperatura minima, maxima y promedio, humedad promedio, precipitacion total y velocidad promedio del viento.
- Guarda los resultados en CSV y realiza UPSERT en PostgreSQL.

## Requisitos

- Python 3.11 o posterior.
- PostgreSQL accesible desde el equipo.
- Acceso a Internet para consultar Open-Meteo.

## Instalacion

Desde la raiz del proyecto, crea y activa un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

En Windows PowerShell, activa el entorno con:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Configuracion

### PostgreSQL

Crea un archivo `.env` en la raiz del proyecto con las credenciales de tu base de datos:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=weather_db
DB_USER=postgres
DB_PASSWORD=change_me
```

No publiques ni subas el archivo `.env` al repositorio. El pipeline requiere las cinco variables y comprueba la conexion antes de comenzar.

Crea las tablas una sola vez en la base de datos configurada. El pipeline crea automaticamente los indices unicos que necesita para actualizar filas existentes.

```sql
CREATE TABLE IF NOT EXISTS weather_hourly (
		city TEXT NOT NULL,
		latitude DOUBLE PRECISION,
		longitude DOUBLE PRECISION,
		datetime TIMESTAMP NOT NULL,
		temperature_c DOUBLE PRECISION,
		humidity_pct DOUBLE PRECISION,
		precipitation_mm DOUBLE PRECISION,
		wind_speed_kmh DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS weather_summary (
		city TEXT NOT NULL,
		temperature_min DOUBLE PRECISION,
		temperature_max DOUBLE PRECISION,
		temperature_avg DOUBLE PRECISION,
		humidity_avg DOUBLE PRECISION,
		precipitation_total DOUBLE PRECISION,
		wind_speed_avg DOUBLE PRECISION
);
```

### Ciudades

Edita `config/cities.json` para agregar o modificar ciudades y sus coordenadas. Cada entrada debe tener `latitude` y `longitude`:

```json
{
	"Bogota": {
		"latitude": 4.711,
		"longitude": -74.0721
	}
}
```

## Ejecucion

Activa el entorno virtual y ejecuta el pipeline desde la raiz del proyecto:

```bash
python -m src.main
```

## Interfaz web

En desarrollo, inicia el servidor de la API desde la raiz del proyecto:

```bash
python -m src.api
```

En otra terminal, inicia el frontend:

```bash
cd frontend
npm install
npm run dev
```

Abre la URL que muestra Vite (normalmente `http://localhost:5173`). Para ejecutar la interfaz compilada, ejecuta `npm run build` dentro de `frontend/` y luego inicia `python -m src.api`; quedara disponible en `http://127.0.0.1:8000`.

## Etapas del pipeline

1. **Extract:** consulta Open-Meteo y guarda la respuesta original.
2. **Transform:** convierte los datos horarios a un DataFrame y valida su calidad y estructura.
3. **Analyze:** calcula el resumen estadistico por ciudad.
4. **Load:** escribe los CSV y actualiza las tablas PostgreSQL mediante UPSERT.

Los UPSERT usan `city` y `datetime` como clave para `weather_hourly`, y `city` para `weather_summary`. Por eso esas columnas deben poder identificar filas unicas; el pipeline crea los indices correspondientes si aun no existen.

## Archivos generados

- `data/raw/weather_<fecha>_<hora>.json`: respuesta original de cada ejecucion; se conserva historicamente.
- `data/processed/weather_processed.csv`: datos horarios procesados; se sobrescribe en cada ejecucion.
- `data/processed/weather_summary.csv`: estadisticas por ciudad; se sobrescribe en cada ejecucion.

Las tablas de PostgreSQL son `weather_hourly` y `weather_summary`.

## Solucion de problemas

- **Faltan variables de entorno:** verifica que `.env` este en la raiz y contenga `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASSWORD`.
- **No se puede conectar a PostgreSQL:** comprueba que el servicio este activo, que el puerto y las credenciales sean correctos y que la base de datos exista.
- **No existe una tabla o columna:** crea las tablas con el esquema de esta guia y confirma que sus nombres y columnas coincidan.
- **No se obtienen datos meteorologicos:** revisa la conexion a Internet y la disponibilidad de Open-Meteo.
