const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api/pipeline'

export const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

export const PIPELINE_STATUS_LABELS = {
  idle: 'Sistema listo',
  running: 'Pipeline en ejecución',
  completed: 'Pipeline completado',
  error: 'Pipeline fallido',
}

export const STAGES = [
  {
    key: 'extract',
    label: 'Extracción',
    duration: 2000,
    title: 'EXTRAYENDO DATOS',
    running: 'Obteniendo el pronóstico horario desde Open-Meteo...',
    done: 'Datos extraídos desde Open-Meteo',
    pending: 'Esperando',
    meta: '5 ciudades · 840 registros',
  },
  {
    key: 'transform',
    label: 'Transformación',
    duration: 6000,
    title: 'TRANSFORMANDO Y VALIDANDO DATOS',
    running: 'Estructurando los datos y comprobando su integridad...',
    done: '1.248 registros procesados y validados',
    pending: 'Esperando',
    meta: '1.248 registros validados',
  },
  {
    key: 'analyze',
    label: 'Análisis',
    duration: 2000,
    title: 'ANALIZANDO DATOS',
    running: 'Calculando las estadísticas de cada ciudad...',
    done: 'Estadísticas calculadas para 5 ciudades',
    pending: 'Esperando',
    meta: '5 ciudades · 6 métricas',
  },
  {
    key: 'load',
    label: 'Carga',
    duration: 3000,
    title: 'CARGANDO DATOS',
    running: 'Escribiendo los archivos CSV y aplicando upsert en PostgreSQL...',
    done: 'Resultados cargados en CSV y PostgreSQL',
    pending: 'Esperando',
    meta: '2 tablas actualizadas',
  },
]

export const TOTAL_DURATION = STAGES.reduce((total, stage) => total + stage.duration, 0)

const TARGET_RECORDS = 1248
const TARGET_CITIES = 5
const EXTRACT_RECORDS = 840

const LOG_EVENTS = [
  { at: 0, level: 'INFO', message: 'Ejecución del pipeline iniciada' },
  { at: 60, level: 'INFO', message: 'Extrayendo datos meteorológicos de Open-Meteo' },
  { at: 800, level: 'INFO', message: 'Obteniendo pronóstico horario de 5 ciudades' },
  { at: 1950, level: 'SUCCESS', message: 'Extracción completada · 840 registros obtenidos' },

  { at: 2050, level: 'INFO', message: 'Transformando registros en filas estructuradas' },
  { at: 3200, level: 'INFO', message: 'Parseando columnas de fecha y ajustando tipos' },
  { at: 4950, level: 'SUCCESS', message: 'Transformación completada · 1.248 registros procesados' },

  { at: 5050, level: 'INFO', message: 'Validando la calidad y la integridad de los datos' },
  { at: 6300, level: 'INFO', message: 'Comprobando campos requeridos, nulos, tipos y rangos' },
  { at: 7950, level: 'SUCCESS', message: 'Transformación y validación completadas · 1.248 registros válidos' },

  { at: 8050, level: 'INFO', message: 'Calculando estadísticas por ciudad' },
  { at: 9950, level: 'SUCCESS', message: 'Análisis completado · 5 ciudades resumidas' },

  { at: 10050, level: 'INFO', message: 'Escribiendo weather_processed.csv y weather_summary.csv' },
  { at: 11200, level: 'INFO', message: 'Aplicando upsert de filas en PostgreSQL' },
  { at: 12950, level: 'SUCCESS', message: 'Carga completada · 1.248 filas persistidas' },
  { at: 13000, level: 'SUCCESS', message: 'Ejecución del pipeline completada en 13.0s' },
]

function formatClock(timestamp) {
  const date = new Date(timestamp)
  return [date.getHours(), date.getMinutes(), date.getSeconds()]
    .map((part) => String(part).padStart(2, '0'))
    .join(':')
}

export function createInitialSnapshot() {
  return {
    status: 'idle',
    errorMessage: null,
    startedAt: null,
    elapsed: 0,
    currentStage: -1,
    stageProgress: 0,
    stages: STAGES.map((stage) => ({
      key: stage.key,
      label: stage.label,
      status: 'pending',
      progress: 0,
      description: stage.pending,
      meta: null,
    })),
    stats: {
      records: 0,
      cities: 0,
      executionTime: '0.0s',
      quality: null,
    },
    logs: [],
  }
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

function computeStageState(elapsed) {
  let cursor = 0
  let index = 0

  while (index < STAGES.length && elapsed >= cursor + STAGES[index].duration) {
    cursor += STAGES[index].duration
    index += 1
  }

  if (index >= STAGES.length) {
    return { index: STAGES.length - 1, progress: 100, allDone: true }
  }

  const stage = STAGES[index]
  const progress = clamp(((elapsed - cursor) / stage.duration) * 100, 0, 100)
  return { index, progress, allDone: false }
}

function computeStats(index, progress, elapsed) {
  const ratio = progress / 100
  let records = 0
  let cities = 0

  if (index >= 1) {
    records = EXTRACT_RECORDS
    cities = TARGET_CITIES
  }

  if (index === 0) {
    records = Math.round(EXTRACT_RECORDS * ratio)
    cities = Math.round(TARGET_CITIES * ratio)
  } else if (index === 1) {
    records = Math.round(EXTRACT_RECORDS + (TARGET_RECORDS - EXTRACT_RECORDS) * ratio)
  } else {
    records = TARGET_RECORDS
  }

  return {
    records,
    cities,
    executionTime: `${(elapsed / 1000).toFixed(1)}s`,
    quality: null,
  }
}

function buildLogs(startedAt, elapsed) {
  return LOG_EVENTS.filter((event) => event.at <= elapsed)
    .map((event, order) => ({
      id: order,
      time: formatClock(startedAt + event.at),
      level: event.level,
      message: event.message,
    }))
}

export function simulateSnapshot(startedAt, elapsed) {
  const safeElapsed = Math.min(elapsed, TOTAL_DURATION)
  const { index, progress, allDone } = computeStageState(safeElapsed)
  const isComplete = safeElapsed >= TOTAL_DURATION

  const stages = STAGES.map((stage, stageIndex) => {
    if (isComplete || stageIndex < index) {
      return {
        key: stage.key,
        label: stage.label,
        status: 'completed',
        progress: 100,
        description: stage.done,
        meta: stage.meta,
      }
    }

    if (stageIndex === index) {
      return {
        key: stage.key,
        label: stage.label,
        status: 'running',
        progress,
        description: stage.running,
        meta: null,
      }
    }

    return {
      key: stage.key,
      label: stage.label,
      status: 'pending',
      progress: 0,
      description: stage.pending,
      meta: null,
    }
  })

  return {
    status: isComplete ? 'completed' : 'running',
    errorMessage: null,
    startedAt,
    elapsed: safeElapsed,
    currentStage: index,
    stageProgress: progress,
    stages,
    stats: computeStats(index, progress, safeElapsed),
    logs: buildLogs(startedAt, safeElapsed),
  }
}

export function startSimulation({ onTick, onError }) {
  const startedAt = Date.now()
  let timer = null

  const tick = () => {
    try {
      const elapsed = Date.now() - startedAt
      const snapshot = simulateSnapshot(startedAt, elapsed)
      onTick(snapshot)

      if (elapsed >= TOTAL_DURATION) {
        clearInterval(timer)
        timer = null
      }
    } catch (error) {
      clearInterval(timer)
      timer = null
      onError?.(error.message)
    }
  }

  timer = setInterval(tick, 80)
  tick()

  return {
    cancel() {
      if (timer) clearInterval(timer)
      timer = null
    },
  }
}

export async function runPipeline() {
  const response = await fetch(`${API_BASE}/run`, { method: 'POST' })
  if (!response.ok) throw new Error(`No se pudo iniciar el pipeline (estado ${response.status})`)
  return response.json()
}

export async function getPipelineStatus() {
  const response = await fetch(`${API_BASE}/status`)
  if (!response.ok) throw new Error(`No se pudo consultar el estado (estado ${response.status})`)
  return response.json()
}

export async function getPipelineLogs() {
  const response = await fetch(`${API_BASE}/logs`)
  if (!response.ok) throw new Error(`No se pudieron obtener los registros (estado ${response.status})`)
  return response.json()
}

const MOCK_RESULTS = {
  summary: [
    { city: 'Barranquilla', temperature_min: 22.8, temperature_max: 32.5, temperature_avg: 26.69, humidity_avg: 87.78, precipitation_total: 61.3, wind_speed_avg: 6.28 },
    { city: 'Cali', temperature_min: 19.5, temperature_max: 28.4, temperature_avg: 22.43, humidity_avg: 86.95, precipitation_total: 78.9, wind_speed_avg: 2.05 },
    { city: 'Medellin', temperature_min: 16.7, temperature_max: 29.3, temperature_avg: 20.7, humidity_avg: 88.92, precipitation_total: 97.1, wind_speed_avg: 2.23 },
    { city: 'Bogota', temperature_min: 10.9, temperature_max: 21.5, temperature_avg: 15.07, humidity_avg: 84.58, precipitation_total: 67.9, wind_speed_avg: 3.19 },
  ],
  hourly: [],
  totalHourly: 672,
  updatedAt: new Date().toISOString().replace('T', ' ').substring(0, 19),
}

export async function getPipelineResults() {
  if (USE_MOCK) return MOCK_RESULTS
  const response = await fetch(`${API_BASE}/results`)
  if (!response.ok) throw new Error(`No se pudieron obtener los resultados (estado ${response.status})`)
  return response.json()
}
