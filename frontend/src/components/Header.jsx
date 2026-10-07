import { Activity, CloudSun } from 'lucide-react'
import { PIPELINE_STATUS_LABELS } from '../services/pipelineApi'

const STATUS_STYLES = {
  idle: {
    dot: 'bg-emerald-500',
    text: 'text-emerald-300',
    border: 'border-emerald-500/40',
    bg: 'bg-emerald-500/10',
  },
  running: {
    dot: 'bg-blue-500',
    text: 'text-blue-300',
    border: 'border-blue-500/40',
    bg: 'bg-blue-500/10',
  },
  completed: {
    dot: 'bg-emerald-500',
    text: 'text-emerald-300',
    border: 'border-emerald-500/40',
    bg: 'bg-emerald-500/10',
  },
  error: {
    dot: 'bg-red-500',
    text: 'text-red-300',
    border: 'border-red-500/40',
    bg: 'bg-red-500/10',
  },
}

export default function Header({ status = 'idle' }) {
  const style = STATUS_STYLES[status] ?? STATUS_STYLES.idle
  const label = PIPELINE_STATUS_LABELS[status] ?? PIPELINE_STATUS_LABELS.idle

  return (
    <header className="border-b border-slate-800/80 bg-[#0a0f1a]/90 backdrop-blur-md sticky top-0 z-20">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3 min-w-0">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-slate-700/80 bg-slate-900 text-blue-400">
            <CloudSun size={20} strokeWidth={1.75} />
          </span>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="truncate text-base font-semibold tracking-tight text-slate-100 sm:text-lg">
                Weather Data Pipeline
              </h1>
              <Activity size={14} className="hidden shrink-0 text-slate-600 sm:block" />
            </div>
            <p className="truncate text-xs text-slate-500 sm:text-sm">Panel de monitoreo ETL</p>
          </div>
        </div>

        <div
          className={`flex shrink-0 items-center gap-2.5 rounded-full border px-3 py-1.5 sm:px-4 ${style.border} ${style.bg}`}
        >
          <span className="relative flex h-2.5 w-2.5">
            <span className={`h-2.5 w-2.5 rounded-full ${style.dot}`} />
            {(status === 'running' || status === 'idle') && (
              <span
                className={`absolute inset-0 rounded-full ${style.dot} animate-ring-pulse`}
                aria-hidden="true"
              />
            )}
          </span>
          <span className={`text-xs font-medium sm:text-sm ${style.text}`}>{label}</span>
        </div>
      </div>
    </header>
  )
}
