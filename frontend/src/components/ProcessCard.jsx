import { CircleCheck, Loader2, Play, TriangleAlert } from 'lucide-react'
import { STAGES } from '../services/pipelineApi'

function formatSeconds(ms) {
  return `${(ms / 1000).toFixed(1)}s`
}

export default function ProcessCard({ snapshot }) {
  const { status, stages, currentStage, stageProgress, elapsed } = snapshot

  const active = status === 'running' ? stages[currentStage] : null
  const definition = active ? STAGES[currentStage] : null

  let title = 'PIPELINE INACTIVO'
  let description = 'Listo para extraer datos meteorológicos de Open-Meteo.'
  let progress = 0
  let tone = 'bg-slate-500'
  let accentText = 'text-slate-300'

  if (status === 'running' && definition) {
    title = definition.title
    description = definition.running
    progress = stageProgress
    tone = 'bg-blue-500'
    accentText = 'text-blue-300'
  } else if (status === 'completed') {
    title = 'PIPELINE COMPLETADO'
    description = 'Las cinco etapas finalizaron correctamente.'
    progress = 100
    tone = 'bg-emerald-500'
    accentText = 'text-emerald-300'
  } else if (status === 'error') {
    title = 'PIPELINE FALLIDO'
    description = snapshot.errorMessage || 'El pipeline se detuvo por un error.'
    progress = stageProgress
    tone = 'bg-red-500'
    accentText = 'text-red-300'
  }

  const roundedProgress = Math.round(progress)

  return (
    <section className="panel flex h-[380px] flex-col justify-between p-5 sm:p-6 animate-fade-up">
      <div className="flex shrink-0 items-center justify-between">
        <div>
          <h2 className="panel-title">Proceso actual</h2>
          <p className="panel-subtitle mt-0.5">Ejecución de la etapa en curso</p>
        </div>
        <span
          className={`flex h-9 w-9 items-center justify-center rounded-lg border border-slate-800 bg-slate-900 ${accentText}`}
        >
          {status === 'running' && <Loader2 size={16} className="animate-spin" />}
          {status === 'completed' && <CircleCheck size={16} />}
          {status === 'error' && <TriangleAlert size={16} />}
          {status === 'idle' && <Play size={16} />}
        </span>
      </div>

      <div className="my-auto py-2">
        <p
          className={`text-xl font-semibold tracking-wide sm:text-2xl ${accentText} transition-colors duration-300`}
        >
          {title}
        </p>
        <p className="mt-1.5 text-sm text-slate-400">{description}</p>
      </div>

      <div className="shrink-0">
        <div className="flex items-end justify-between">
          <span className="text-xs font-medium uppercase tracking-wider text-slate-500">
            Progreso
          </span>
          <span className="font-mono text-2xl font-semibold tabular-nums text-slate-100">
            {roundedProgress}%
          </span>
        </div>

        <div className="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-slate-800/90">
          <div
            className={`h-full rounded-full transition-[width] duration-200 ease-linear ${tone}`}
            style={{ width: `${roundedProgress}%` }}
          />
        </div>

        <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
          <span>Tiempo transcurrido</span>
          <span className="font-mono tabular-nums text-slate-400">{formatSeconds(elapsed)}</span>
        </div>
      </div>
    </section>
  )
}
