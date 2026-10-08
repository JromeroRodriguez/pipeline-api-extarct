const CIRCLE_STYLES = {
  pending: 'border-slate-700 bg-[#111827] text-slate-500',
  running: 'border-blue-500/70 bg-blue-500/15 text-blue-400',
  completed: 'border-emerald-500/60 bg-emerald-500/15 text-emerald-400',
  error: 'border-red-500/60 bg-red-500/15 text-red-400',
}

const LABEL_STYLES = {
  pending: 'text-slate-500',
  running: 'text-blue-300',
  completed: 'text-slate-200',
  error: 'text-red-300',
}

const STATUS_TEXT = {
  pending: 'Esperando',
  running: 'Procesando...',
  completed: 'Completado',
  error: 'Fallido',
}

function Connector({ status }) {
  const color =
    status === 'completed'
      ? 'bg-emerald-500/60 pipeline-connector-complete'
      : status === 'error'
        ? 'bg-red-500/60'
        : 'bg-slate-800'

  return (
    <>
      <span
        aria-hidden="true"
        className={`hidden h-0.5 min-w-4 flex-1 rounded-full transition-colors duration-300 md:mt-5 md:block ${color}`}
      />
      <span
        aria-hidden="true"
        className={`ml-5 h-6 w-0.5 shrink-0 rounded-full transition-colors duration-300 md:hidden ${color}`}
      />
    </>
  )
}

export default function PipelineProgress({ stages }) {
  return (
    <div className="mx-auto flex w-full max-w-4xl flex-col md:flex-row md:items-start md:px-4">
      {stages.map((stage, index) => {
        const completionAnimation =
          stage.status === 'completed' ? 'animate-stage-complete' : ''

        return (
          <div key={stage.key} className="contents">
            {index > 0 && <Connector status={stages[index - 1].status} />}

            <div className="flex min-w-0 items-center gap-4 md:flex-1 md:flex-col md:gap-2 md:text-center">
              <span
                aria-label={`${stage.label}: ${STATUS_TEXT[stage.status]}`}
                aria-current={stage.status === 'running' ? 'step' : undefined}
                className={`relative flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-2 text-sm font-medium transition-colors duration-300 ${
                  CIRCLE_STYLES[stage.status]
                } ${completionAnimation}`}
              >
                {stage.status === 'running' && (
                  <span
                    aria-hidden="true"
                    className="absolute inset-0 rounded-full border-2 border-blue-500/40 animate-ring-pulse"
                  />
                )}
                {index + 1}
              </span>

              <div className="min-w-0 flex-1 md:flex-none">
                <p
                  className={`text-sm font-semibold transition-colors duration-300 ${
                    LABEL_STYLES[stage.status]
                  }`}
                >
                  {stage.label}
                </p>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
