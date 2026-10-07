import { useCallback, useEffect, useRef, useState } from 'react'
import {
  USE_MOCK,
  createInitialSnapshot,
  getPipelineLogs,
  getPipelineStatus,
  runPipeline,
  startSimulation,
} from '../services/pipelineApi'

export function usePipeline() {
  const [snapshot, setSnapshot] = useState(() => createInitialSnapshot())
  const simulationRef = useRef(null)
  const pollingRef = useRef(null)

  const teardown = useCallback(() => {
    simulationRef.current?.cancel()
    simulationRef.current = null

    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }, [])

  const startPolling = useCallback(() => {
    pollingRef.current = setInterval(async () => {
      try {
        const [status, logs] = await Promise.all([getPipelineStatus(), getPipelineLogs()])
        setSnapshot((previous) => ({
          ...previous,
          ...status,
          logs: logs?.entries ?? previous.logs,
        }))

        if (status.status !== 'running') {
          clearInterval(pollingRef.current)
          pollingRef.current = null
        }
      } catch (error) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
        setSnapshot((previous) => ({
          ...previous,
          status: 'error',
          errorMessage: error.message,
        }))
      }
    }, 800)
  }, [])

  const run = useCallback(async () => {
    teardown()
    setSnapshot((previous) => ({
      ...createInitialSnapshot(),
      status: 'running',
      startedAt: Date.now(),
    }))

    if (USE_MOCK) {
      simulationRef.current = startSimulation({
        onTick: setSnapshot,
        onError: (message) =>
          setSnapshot((previous) => ({ ...previous, status: 'error', errorMessage: message })),
      })
      return
    }

    try {
      await runPipeline()
      startPolling()
    } catch (error) {
      setSnapshot((previous) => ({
        ...previous,
        status: 'error',
        errorMessage: error.message,
      }))
    }
  }, [startPolling, teardown])

  const reset = useCallback(() => {
    teardown()
    setSnapshot(createInitialSnapshot())
  }, [teardown])

  useEffect(() => teardown, [teardown])

  return {
    ...snapshot,
    isRunning: snapshot.status === 'running',
    run,
    reset,
  }
}
