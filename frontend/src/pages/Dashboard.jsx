import ExecutionLogs from '../components/ExecutionLogs'
import Header from '../components/Header'
import PipelineProgress from '../components/PipelineProgress'
import ProcessCard from '../components/ProcessCard'
import RunPipelineButton from '../components/RunPipelineButton'
import { usePipeline } from '../hooks/usePipeline'

export default function Dashboard() {
  const pipeline = usePipeline()
  const { stages, logs, status, run } = pipeline

  return (
    <div className="relative min-h-screen">
      <div className="relative">
        <Header status={status} />

        <main className="mx-auto max-w-6xl space-y-6 px-4 pb-16 pt-6 md:px-8">
          <section className="panel p-5 sm:p-6 animate-fade-up">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="panel-title">Estado del pipeline</h2>
                <p className="panel-subtitle mt-0.5">
                  Extracción → Transformación → Validación → Análisis → Carga
                </p>
              </div>
            </div>
            <div className="mt-6">
              <PipelineProgress stages={stages} />
            </div>
          </section>

          <div className="grid grid-cols-1 items-stretch gap-6 lg:grid-cols-2">
            <ProcessCard snapshot={pipeline} />
            <ExecutionLogs logs={logs} />
          </div>

          <div className="flex justify-center pt-2">
            <RunPipelineButton status={status} onRun={run} />
          </div>
        </main>
      </div>
    </div>
  )
}
