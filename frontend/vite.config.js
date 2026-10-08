import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

function parseCsv(content) {
  const lines = content.trim().split('\n')
  if (lines.length < 2) return []
  const headers = lines[0].split(',').map((h) => h.trim())
  return lines.slice(1).map((line) => {
    const values = line.split(',').map((v) => v.trim())
    const obj = {}
    headers.forEach((h, i) => {
      const val = values[i]
      const num = Number(val)
      obj[h] = !isNaN(num) && val !== '' ? num : val
    })
    return obj
  })
}

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    {
      name: 'results-api-middleware',
      configureServer(server) {
        server.middlewares.use('/api/pipeline/results', (req, res, next) => {
          try {
            const summaryPath = path.resolve(__dirname, '../data/processed/weather_summary.csv')
            const processedPath = path.resolve(__dirname, '../data/processed/weather_processed.csv')
            let summary = []
            let hourly = []
            let totalHourly = 0
            let updatedAt = null

            if (fs.existsSync(summaryPath)) {
              const content = fs.readFileSync(summaryPath, 'utf-8')
              summary = parseCsv(content)
              const stat = fs.statSync(summaryPath)
              updatedAt = stat.mtime.toISOString().replace('T', ' ').substring(0, 19)
            }

            if (fs.existsSync(processedPath)) {
              const content = fs.readFileSync(processedPath, 'utf-8')
              const allHourly = parseCsv(content)
              totalHourly = allHourly.length
              hourly = allHourly.slice(0, 200)
            }

            res.setHeader('Content-Type', 'application/json; charset=utf-8')
            res.end(JSON.stringify({ summary, hourly, totalHourly, updatedAt }))
          } catch (err) {
            next(err)
          }
        })
      },
    },
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
