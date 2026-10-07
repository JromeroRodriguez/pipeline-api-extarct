import { Check, Circle, X } from 'lucide-react'

const NODE_STYLES = {
  pending: 'border-slate-700 bg-slate-900 text-slate-600',
  running: 'border-blue-500/70 bg-blue-500/15 text-blue-400',
  completed: 'border-emerald-500/60 bg-emerald-500/15 text-emerald-400',
  error: 'border-red-500/60 bg-red-500/15 text-red-400',
}

const TITLE_STYLES = {
  pending: 'text-slate-500',
  running: 'text-blue-200',
  completed: 'text-slate-100',
  error: 'text-red-300',
}

function NodeIcon({ status }) {
  if (status === 'completed') return <Check size={15} strokeWidth={2.5} />
  if (status === 'error') return <X size={15} strokeWidth={2.5} />
  if (status === 'running') return <span className="h-2 w-2 rounded-full bg-blue-400 animate-pulse" />
  return <Circle size={13} strokeWidth={2} />
}

function railColor(status) {
  if (status === 'completed') return 'bg-emerald-500/40'
  if (status === 'error') return 'bg-red-500/40'
  if (status === 'running') return 'bg-blue-500/40'
  return 'bg-slate-800'
}

export default function ExecutionTimeline({ stages }) {
  return (
    <section className="panel p-5 sm:p-6 h-full animate-fade-up">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="panel-title">Ejecución del pipeline</h2>
          <p className="panel-subtitle mt-0.5">Actividad por etapa</p>
        </div>
      </div>

      <ol className="mt-6">
        {stages.map((stage, index) => {
          const isLast = index === stages.length - 1
          const meta =
            stage.status === 'completed'
              ? stage.meta
              : stage.status === 'running'
                ? `${Math.round(stage.progress)}%`
                : stage.status === 'error'
                  ? 'Detenida'
                  : 'En espera'

          return (
            <li key={stage.key} className="relative flex gap-4 pb-6 last:pb-0">
              {!isLast && (
                <span
                  aria-hidden="true"
                  className={`absolute left-4 top-8 bottom-0 w-px ${railColor(stage.status)}`}
                />
              )}

              <span
                className={`relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border transition-colors duration-300 ${
                  NODE_STYLES[stage.status]
                }`}
              >
                <NodeIcon status={stage.status} />
              </span>

              <div className="min-w-0 flex-1 pt-0.5">
                <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
                  <h3
                    className={`text-sm font-semibold transition-colors duration-300 ${
                      TITLE_STYLES[stage.status]
                    }`}
                  >
                    {stage.label}
                  </h3>
                  <span
                    className={`font-mono text-xs tabular-nums ${
                      stage.status === 'pending' ? 'text-slate-600' : 'text-slate-500'
                    }`}
                  >
                    {meta}
                  </span>
                </div>

                <p
                  className={`mt-1 text-sm ${
                    stage.status === 'pending' ? 'text-slate-600' : 'text-slate-400'
                  }`}
                >
                  {stage.description}
                </p>

                {stage.status === 'running' && (
                  <div className="mt-2.5 h-1 w-full max-w-xs overflow-hidden rounded-full bg-slate-800">
                    <div
                      className="h-full rounded-full bg-blue-500 transition-[width] duration-200 ease-linear"
                      style={{ width: `${Math.round(stage.progress)}%` }}
                    />
                  </div>
                )}
              </div>
            </li>
          )
        })}
      </ol>
    </section>
  )
}
