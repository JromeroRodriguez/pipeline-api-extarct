import { Loader2, Play, RefreshCw, RotateCcw } from 'lucide-react'

const STATES = {
  idle: {
    label: 'Ejecutar pipeline',
    icon: Play,
    className: 'bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-950/50',
  },
  running: {
    label: 'Ejecutando pipeline...',
    icon: Loader2,
    className: 'bg-blue-600/50 text-blue-100 cursor-not-allowed',
  },
  completed: {
    label: 'Volver a ejecutar',
    icon: RefreshCw,
    className: 'bg-slate-100 hover:bg-white text-slate-900 shadow-lg shadow-slate-950/50',
  },
  error: {
    label: 'Reintentar pipeline',
    icon: RotateCcw,
    className: 'bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-950/50',
  },
}

export default function RunPipelineButton({ status = 'idle', disabled = false, onRun }) {
  const config = STATES[status] ?? STATES.idle
  const Icon = config.icon
  const isRunning = status === 'running'

  return (
    <div className="flex flex-col items-center gap-3">
      <button
        type="button"
        onClick={onRun}
        disabled={disabled || isRunning}
        className={`inline-flex h-12 min-w-56 items-center justify-center gap-2.5 rounded-lg px-8 text-sm font-semibold tracking-wide transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/60 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0a0f1a] disabled:opacity-90 active:scale-[0.98] ${config.className}`}
      >
        <Icon size={17} strokeWidth={2.25} className={isRunning ? 'animate-spin' : ''} />
        {config.label}
      </button>

      <p className="text-xs text-slate-600">
        {isRunning
          ? 'El pipeline está en ejecución. Consulta el progreso arriba.'
          : 'Extracción · Transformación · Análisis · Carga'}
      </p>
    </div>
  )
}
