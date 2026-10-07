import { Database, MapPin, ShieldCheck, Timer } from 'lucide-react'

function Metric({ icon: Icon, label, value }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900/50 p-4">
      <div className="flex items-center gap-2 text-slate-500">
        <Icon size={14} strokeWidth={2} />
        <span className="text-xs font-medium uppercase tracking-wider">{label}</span>
      </div>
      <p className="mt-2 font-mono text-2xl font-semibold tabular-nums text-slate-100">{value}</p>
    </div>
  )
}

export default function StatisticsCard({ stats }) {
  const records = new Intl.NumberFormat('es-CO').format(stats.records)
  const quality = stats.quality === null ? '--' : `${stats.quality}%`

  return (
    <section className="panel p-5 sm:p-6 animate-fade-up" style={{ animationDelay: '80ms' }}>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="panel-title">Estadísticas del pipeline</h2>
          <p className="panel-subtitle mt-0.5">Actualizadas en tiempo real</p>
        </div>
        <span className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-800 bg-slate-900 text-slate-400">
          <Database size={16} />
        </span>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2">
        <Metric icon={Database} label="Registros procesados" value={records} />
        <Metric icon={MapPin} label="Ciudades" value={String(stats.cities)} />
        <Metric icon={Timer} label="Tiempo de ejecución" value={stats.executionTime} />
        <Metric icon={ShieldCheck} label="Calidad de datos" value={quality} />
      </div>
    </section>
  )
}
