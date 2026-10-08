import { useEffect, useRef } from 'react'
import { TerminalSquare } from 'lucide-react'

const LEVEL_STYLES = {
  INFO: 'text-sky-400',
  SUCCESS: 'text-emerald-400',
  WARNING: 'text-amber-400',
  ERROR: 'text-red-400',
}

const LEVEL_LABELS = {
  INFO: 'INFO',
  SUCCESS: 'ÉXITO',
  WARNING: 'AVISO',
  ERROR: 'ERROR',
}

export default function ExecutionLogs({ logs }) {
  const scrollRef = useRef(null)

  useEffect(() => {
    const node = scrollRef.current
    if (node) node.scrollTop = node.scrollHeight
  }, [logs])

  return (
    <section
      className="panel flex h-[380px] flex-col p-5 sm:p-6 animate-fade-up"
      style={{ animationDelay: '60ms' }}
    >
      <div className="flex shrink-0 items-center justify-between">
        <div>
          <h2 className="panel-title">Registros de ejecución</h2>
          <p className="panel-subtitle mt-0.5">Eventos del pipeline con marca de tiempo</p>
        </div>
        <span className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-800 bg-slate-900 text-slate-400">
          <TerminalSquare size={16} />
        </span>
      </div>

      <div
        ref={scrollRef}
        className="logs-scroll mt-5 min-h-0 flex-1 overflow-y-auto rounded-lg border border-slate-800/80 bg-black/40 p-4 font-mono text-xs leading-6"
      >
        {logs.length === 0 ? (
          <p className="text-slate-600">
            Aún no hay registros. Ejecuta el pipeline para ver la actividad.
          </p>
        ) : (
          <ul className="space-y-1">
            {logs.map((log) => (
              <li key={`${log.time}-${log.id}`} className="flex gap-3 animate-enter">
                <span className="shrink-0 tabular-nums text-slate-600">{log.time}</span>
                <span className={`w-16 shrink-0 font-semibold ${LEVEL_STYLES[log.level]}`}>
                  {LEVEL_LABELS[log.level] ?? log.level}
                </span>
                <span className="min-w-0 break-words text-slate-400">{log.message}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
