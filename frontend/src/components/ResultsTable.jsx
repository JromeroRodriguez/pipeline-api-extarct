import { useState, useMemo } from 'react'
import {
  Table as TableIcon,
  Download,
  RefreshCw,
  MapPin,
  ThermometerSnowflake,
  ThermometerSun,
  Droplets,
  CloudRain,
  Wind,
  ChevronLeft,
  ChevronRight,
  Database,
  Calendar,
} from 'lucide-react'

function downloadCsv(data, filename) {
  if (!data || data.length === 0) return
  const headers = Object.keys(data[0])
  const csvRows = [
    headers.join(','),
    ...data.map((row) =>
      headers
        .map((h) => {
          const val = row[h] ?? ''
          return typeof val === 'string' && val.includes(',') ? `"${val}"` : val
        })
        .join(',')
    ),
  ]
  const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

export default function ResultsTable({ results, loading, onRefresh, pipelineStatus }) {
  const [activeTab, setActiveTab] = useState('summary') // 'summary' | 'hourly'
  const [selectedCity, setSelectedCity] = useState('ALL')
  const [page, setPage] = useState(1)
  const pageSize = 10

  const summary = results?.summary || []
  const hourly = results?.hourly || []
  const totalHourly = results?.totalHourly || hourly.length
  const updatedAt = results?.updatedAt

  const filteredHourly = useMemo(() => {
    if (selectedCity === 'ALL') return hourly
    return hourly.filter((item) => item.city === selectedCity)
  }, [hourly, selectedCity])

  const totalPages = Math.ceil(filteredHourly.length / pageSize) || 1
  const paginatedHourly = useMemo(() => {
    const start = (page - 1) * pageSize
    return filteredHourly.slice(start, start + pageSize)
  }, [filteredHourly, page, pageSize])

  const handleCityChange = (e) => {
    setSelectedCity(e.target.value)
    setPage(1)
  }

  const handleDownload = () => {
    if (activeTab === 'summary') {
      downloadCsv(summary, 'weather_summary.csv')
    } else {
      downloadCsv(filteredHourly, 'weather_hourly_preview.csv')
    }
  }

  const hasData = summary.length > 0

  return (
    <section className="panel overflow-hidden p-5 sm:p-6 animate-fade-up" style={{ animationDelay: '100ms' }}>
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg border border-sky-500/30 bg-sky-500/10 text-sky-400">
              <TableIcon size={15} />
            </span>
            <h2 className="text-base font-semibold text-slate-100">Resultados reales del pipeline</h2>
          </div>
          <p className="panel-subtitle mt-1">
            Métricas meteorológicas consolidadas por ciudad generadas por el pipeline ETL
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {updatedAt && (
            <span className="inline-flex items-center gap-1.5 rounded-md border border-slate-800 bg-slate-900/80 px-2.5 py-1 text-xs text-slate-400 font-mono">
              <Calendar size={12} className="text-slate-500" />
              {updatedAt}
            </span>
          )}

          <button
            onClick={onRefresh}
            disabled={loading}
            title="Recargar resultados"
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-700/80 hover:text-white transition-colors disabled:opacity-50"
          >
            <RefreshCw size={13} className={loading ? 'animate-spin text-sky-400' : ''} />
            <span>Refrescar</span>
          </button>

          {hasData && (
            <button
              onClick={handleDownload}
              title="Descargar CSV"
              className="flex items-center gap-1.5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-1.5 text-xs font-medium text-emerald-300 hover:bg-emerald-500/20 transition-colors"
            >
              <Download size={13} />
              <span>Descargar CSV</span>
            </button>
          )}
        </div>
      </div>

      {/* Tabs and Controls */}
      <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex rounded-lg border border-slate-800 bg-slate-900/60 p-1">
          <button
            onClick={() => {
              setActiveTab('summary')
              setPage(1)
            }}
            className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
              activeTab === 'summary'
                ? 'bg-sky-500/20 text-sky-300 shadow-sm border border-sky-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Resumen por ciudad ({summary.length})
          </button>
          {hourly.length > 0 && (
            <button
              onClick={() => {
                setActiveTab('hourly')
                setPage(1)
              }}
              className={`rounded-md px-3 py-1.5 text-xs font-medium transition-colors ${
                activeTab === 'hourly'
                  ? 'bg-sky-500/20 text-sky-300 shadow-sm border border-sky-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Registros horarios ({totalHourly})
            </button>
          )}
        </div>

        {activeTab === 'hourly' && hourly.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">Filtrar ciudad:</span>
            <select
              value={selectedCity}
              onChange={handleCityChange}
              className="rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-sky-500"
            >
              <option value="ALL">Todas las ciudades</option>
              {Array.from(new Set(hourly.map((h) => h.city))).map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Table Content */}
      <div className="mt-4">
        {!hasData ? (
          <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-slate-800 bg-slate-900/20 py-12 text-center">
            <Database size={32} className="text-slate-600 mb-2" />
            <p className="text-sm font-medium text-slate-400">No hay datos procesados disponibles</p>
            <p className="text-xs text-slate-600 mt-1 max-w-sm">
              Haz clic en <span className="text-sky-400 font-semibold">Ejecutar pipeline</span> para consultar Open-Meteo, transformar y consolidar las estadísticas meteorológicas.
            </p>
          </div>
        ) : activeTab === 'summary' ? (
          <div className="overflow-x-auto rounded-lg border border-slate-800/80 bg-slate-900/30">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-800 bg-slate-900/80 text-[11px] uppercase tracking-wider text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-semibold">Ciudad</th>
                  <th className="px-4 py-3 font-semibold">
                    <span className="flex items-center gap-1 text-sky-400">
                      <ThermometerSnowflake size={13} /> Temp. Mín
                    </span>
                  </th>
                  <th className="px-4 py-3 font-semibold">
                    <span className="flex items-center gap-1 text-amber-400">
                      <ThermometerSun size={13} /> Temp. Máx
                    </span>
                  </th>
                  <th className="px-4 py-3 font-semibold">Temp. Prom</th>
                  <th className="px-4 py-3 font-semibold">
                    <span className="flex items-center gap-1 text-emerald-400">
                      <Droplets size={13} /> Humedad Prom
                    </span>
                  </th>
                  <th className="px-4 py-3 font-semibold">
                    <span className="flex items-center gap-1 text-cyan-400">
                      <CloudRain size={13} /> Lluvia Total
                    </span>
                  </th>
                  <th className="px-4 py-3 font-semibold">
                    <span className="flex items-center gap-1 text-indigo-400">
                      <Wind size={13} /> Viento Prom
                    </span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {summary.map((row, index) => (
                  <tr
                    key={row.city || index}
                    className="hover:bg-slate-800/40 transition-colors"
                  >
                    <td className="px-4 py-3 font-sans font-semibold text-slate-200">
                      <span className="flex items-center gap-2">
                        <MapPin size={13} className="text-sky-400" />
                        {row.city}
                      </span>
                    </td>
                    <td className="px-4 py-3 tabular-nums font-medium text-sky-400">
                      {row.temperature_min != null ? `${row.temperature_min} °C` : '--'}
                    </td>
                    <td className="px-4 py-3 tabular-nums font-medium text-amber-400">
                      {row.temperature_max != null ? `${row.temperature_max} °C` : '--'}
                    </td>
                    <td className="px-4 py-3 tabular-nums text-slate-300">
                      {row.temperature_avg != null ? `${row.temperature_avg} °C` : '--'}
                    </td>
                    <td className="px-4 py-3 tabular-nums text-emerald-400">
                      {row.humidity_avg != null ? `${row.humidity_avg} %` : '--'}
                    </td>
                    <td className="px-4 py-3 tabular-nums text-cyan-400">
                      {row.precipitation_total != null ? `${row.precipitation_total} mm` : '--'}
                    </td>
                    <td className="px-4 py-3 tabular-nums text-indigo-300">
                      {row.wind_speed_avg != null ? `${row.wind_speed_avg} km/h` : '--'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div>
            <div className="overflow-x-auto rounded-lg border border-slate-800/80 bg-slate-900/30">
              <table className="w-full text-left text-xs">
                <thead className="border-b border-slate-800 bg-slate-900/80 text-[11px] uppercase tracking-wider text-slate-400">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Ciudad</th>
                    <th className="px-4 py-3 font-semibold">Fecha y Hora</th>
                    <th className="px-4 py-3 font-semibold">Temperatura</th>
                    <th className="px-4 py-3 font-semibold">Humedad</th>
                    <th className="px-4 py-3 font-semibold">Precipitación</th>
                    <th className="px-4 py-3 font-semibold">Viento</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {paginatedHourly.map((row, idx) => (
                    <tr key={`${row.city}-${row.datetime}-${idx}`} className="hover:bg-slate-800/40 transition-colors">
                      <td className="px-4 py-2.5 font-sans font-medium text-slate-200">
                        {row.city}
                      </td>
                      <td className="px-4 py-2.5 text-slate-400 tabular-nums">
                        {row.datetime}
                      </td>
                      <td className="px-4 py-2.5 tabular-nums text-slate-200">
                        {row.temperature_c != null ? `${row.temperature_c} °C` : '--'}
                      </td>
                      <td className="px-4 py-2.5 tabular-nums text-emerald-400">
                        {row.humidity_pct != null ? `${row.humidity_pct} %` : '--'}
                      </td>
                      <td className="px-4 py-2.5 tabular-nums text-cyan-400">
                        {row.precipitation_mm != null ? `${row.precipitation_mm} mm` : '--'}
                      </td>
                      <td className="px-4 py-2.5 tabular-nums text-indigo-300">
                        {row.wind_speed_kmh != null ? `${row.wind_speed_kmh} km/h` : '--'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="mt-3 flex items-center justify-between text-xs text-slate-400 px-1">
                <span>
                  Mostrando {(page - 1) * pageSize + 1} -{' '}
                  {Math.min(page * pageSize, filteredHourly.length)} de {filteredHourly.length} filas
                </span>
                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="flex h-7 w-7 items-center justify-center rounded border border-slate-700 bg-slate-800 text-slate-300 disabled:opacity-40 hover:bg-slate-700 transition-colors"
                  >
                    <ChevronLeft size={14} />
                  </button>
                  <span className="px-2 font-mono tabular-nums">
                    {page} / {totalPages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="flex h-7 w-7 items-center justify-center rounded border border-slate-700 bg-slate-800 text-slate-300 disabled:opacity-40 hover:bg-slate-700 transition-colors"
                  >
                    <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  )
}
