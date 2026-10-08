// Render timing for the hexagon layer: the [render] switch log and the console benchmarks.
//
// Benchmarks, run from the browser console (keep the tab visible while they run):
//   await benchmarkZoom()  -> current category x mode
//   await benchmarkAll()   -> every category x mode of the dataset, downloads a CSV
//   benchmarkCsv()         -> download what benchmarkAll() has saved so far

import { PMTiles } from 'pmtiles'

const BENCHMARK_ZOOMS = [5, 8, 11]
const BENCHMARK_CENTER = [10.4097, 51.4938]
const BENCHMARK_TIMEOUT_MS = 60000

let latestTimingId = 0

export function startTiming() {
  return ++latestTimingId
}

export function logSwitchRendered(map, { timingId, label, start, metadataMs }) {
  const logRendered = () => {
    if (timingId !== latestTimingId) return // superseded by a newer switch or benchmark
    const totalMs = performance.now() - start
    console.log(
      `[render] ${label} visible after ${(totalMs / 1000).toFixed(2)} s ` +
      `(metadata ${metadataMs.toFixed(0)} ms, tiles + draw ${(totalMs - metadataMs).toFixed(0)} ms)`
    )
  }

  if (map.loaded()) logRendered()
  else map.once('idle', logRendered)
}

function waitForIdle(map, timeoutMs = BENCHMARK_TIMEOUT_MS) {
  return new Promise(resolve => {
    const timer = setTimeout(() => {
      map.off('idle', onIdle)
      resolve(false)
    }, timeoutMs)
    const onIdle = () => {
      clearTimeout(timer)
      resolve(true)
    }
    map.once('idle', onIdle)
    map.triggerRepaint()
  })
}

function median(values) {
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2
}

function benchmarkSteps(zooms) {
  return [`z${zooms[0]}_load`, ...zooms.slice(1).map((z, i) => `z${zooms[i]}_to_z${z}`)]
}

function benchmarkSettings({ zooms = BENCHMARK_ZOOMS, center = BENCHMARK_CENTER, repeats = 1 } = {}) {
  return { zooms, center, repeats }
}

function toCsv(rows) {
  const columns = Object.keys(rows[0] ?? {})
  return [columns, ...rows.map(r => columns.map(c => r[c] ?? ''))]
    .map(line => line.join(','))
    .join('\n')
}

function downloadCsv(csv, filename) {
  const link = document.createElement('a')
  link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
  link.download = filename
  link.click()
  URL.revokeObjectURL(link.href)
}

function progressKey(dataset, { zooms, center, repeats }) {
  return `mapper-benchmark:${dataset}:z${zooms.join('-')}:r${repeats}:c${center.join(',')}`
}

function loadProgress(key) {
  try {
    const saved = JSON.parse(localStorage.getItem(key))
    if (saved?.rows && saved?.skipped) return saved
  } catch { /* unavailable or corrupt: start empty */ }
  return { rows: [], skipped: [] }
}

function saveProgress(key, progress) {
  try {
    localStorage.setItem(key, JSON.stringify(progress))
  } catch (err) {
    console.warn('[benchmark] could not save progress, an interrupted run will start over', err)
  }
}

function summarize(rows, dataset, steps) {
  const ok = rows.filter(r => r.status === 'ok')
  return ['median', 'mean'].map(stat => {
    const row = { dataset, category: 'ALL', mode: stat, status: `${ok.length} ok` }
    for (const step of steps) {
      const values = ok.map(r => r[`${step}_ms`])
      const value = stat === 'median' ? median(values) : values.reduce((a, b) => a + b, 0) / values.length
      row[`${step}_ms`] = values.length ? Math.round(value) : ''
    }
    return row
  })
}

// ctx connects the benchmark to the map component:
//   map()            maplibre map, or null
//   dataset()        selected dataset key, or null while not ready
//   metadata()       dataset metadata.json ({ categories, modes })
//   currentCombo()   { category, mode } currently selected
//   tileUrl(layer)   pmtiles http URL for a category_mode layer
//   showLayer(layer) add the hexagon source + layer for category_mode
//   hideLayer()      remove the hexagon source + layer
//   restoreLayer()   show the user's selected layer again
export function createBenchmark(ctx) {
  async function measureLayer(layerName, { zooms, center, repeats }) {
    const map = ctx.map()
    const steps = benchmarkSteps(zooms)
    const times = Object.fromEntries(steps.map(step => [step, []]))

    try {
      await new PMTiles(ctx.tileUrl(layerName)).getHeader()
    } catch {
      return { status: 'missing', times }
    }

    for (let run = 1; run <= repeats; run++) {
      // Start at the first zoom without hexagons (base map is already cached)
      ctx.hideLayer()
      map.jumpTo({ center, zoom: zooms[0] })
      await waitForIdle(map)

      // Fresh source = empty tile cache, so every run loads its tiles again
      let start = performance.now()
      ctx.showLayer(layerName)
      if (!(await waitForIdle(map))) return { status: 'timeout', times }
      times[steps[0]].push(performance.now() - start)

      for (const [i, zoom] of zooms.slice(1).entries()) {
        start = performance.now()
        map.jumpTo({ center, zoom })
        if (!(await waitForIdle(map))) return { status: 'timeout', times }
        times[steps[i + 1]].push(performance.now() - start)
      }
    }

    return { status: 'ok', times }
  }

  async function runBenchmark(combos, { resume = false, fresh = false, download = false, ...options } = {}) {
    const map = ctx.map()
    const dataset = ctx.dataset()
    if (!map || !dataset) {
      console.warn('[benchmark] map or dataset not ready yet')
      return
    }

    const settings = benchmarkSettings(options)
    const { zooms, center, repeats } = settings
    const steps = benchmarkSteps(zooms)
    const key = progressKey(dataset, settings)

    if (fresh) {
      try { localStorage.removeItem(key) } catch { /* nothing saved */ }
    }
    const progress = resume ? loadProgress(key) : { rows: [], skipped: [] }
    const done = new Set([...progress.rows.map(r => `${r.category}_${r.mode}`), ...progress.skipped])
    const todo = combos.filter(({ category, mode }) => !done.has(`${category}_${mode}`))

    startTiming() // drop any pending switch log
    const previousView = { center: map.getCenter(), zoom: map.getZoom() }
    const startedAt = performance.now()

    console.log(
      `[benchmark] ${dataset}: ${combos.length} category x mode, zooms ${zooms.join(', ')}, ` +
      `${repeats} run(s) each. Keep this tab visible until it finishes.`
    )
    if (done.size) {
      console.log(
        `[benchmark] resuming: ${done.size} already done, ${todo.length} to go ` +
        `(benchmarkAll({ fresh: true }) starts over)`
      )
    }

    if (todo.length) {
      // Load the base map at every zoom once, so it is cached and only hexagons are timed
      ctx.hideLayer()
      for (const zoom of zooms) {
        map.jumpTo({ center, zoom })
        await waitForIdle(map)
      }
    }

    for (const [i, { category, mode }] of todo.entries()) {
      const { status, times } = await measureLayer(`${category}_${mode}`, { zooms, center, repeats })

      if (status === 'missing') {
        progress.skipped.push(`${category}_${mode}`)
        if (resume) saveProgress(key, progress)
        continue
      }

      const row = { dataset, category, mode, status }
      for (const step of steps) {
        const t = times[step]
        row[`${step}_ms`] = t.length ? Math.round(median(t)) : ''
        if (repeats > 1) {
          row[`${step}_min_ms`] = t.length ? Math.round(Math.min(...t)) : ''
          row[`${step}_max_ms`] = t.length ? Math.round(Math.max(...t)) : ''
        }
      }
      progress.rows.push(row)
      if (resume) saveProgress(key, progress)

      const elapsed = performance.now() - startedAt
      const remainingMin = (elapsed / (i + 1)) * (todo.length - i - 1) / 60000
      console.log(
        `[benchmark] ${done.size + i + 1}/${combos.length} ${category} / ${mode}: ${status} ` +
        steps.map(step => `${step} ${row[`${step}_ms`] || '-'} ms`).join(', ') +
        ` (about ${remainingMin.toFixed(1)} min left)`
      )
    }

    if (todo.length) {
      // Back to what the user had selected
      ctx.restoreLayer()
      map.jumpTo(previousView)
    }

    const { rows, skipped } = progress
    const summary = summarize(rows, dataset, steps)

    if (skipped.length) console.log(`[benchmark] skipped ${skipped.length} without tiles: ${skipped.join(', ')}`)
    console.table(rows)
    console.log('[benchmark] overall (across all category x mode):')
    console.table(summary)
    if (download) downloadCsv(toCsv([...rows, ...summary]), `benchmark_${dataset}.csv`)
    console.log(`[benchmark] done in ${((performance.now() - startedAt) / 60000).toFixed(1)} min`)
    return { rows, summary }
  }

  function benchmarkZoom(options = {}) {
    return runBenchmark([ctx.currentCombo()], { repeats: 3, ...options })
  }

  // Options: categories / modes (arrays) to benchmark a subset, repeats, zooms, center,
  // fresh (ignore saved progress), download
  function benchmarkAll({ categories, modes, ...options } = {}) {
    const allCategories = categories ?? ctx.metadata()?.categories ?? []
    const allModes = modes ?? ctx.metadata()?.modes ?? []
    const combos = allCategories.flatMap(category => allModes.map(mode => ({ category, mode })))
    return runBenchmark(combos, { resume: true, download: true, ...options })
  }

  // Downloads what benchmarkAll() has saved so far (works during or after a run).
  // Pass the same zooms / center / repeats as the run, if you changed them.
  function benchmarkCsv(options = {}) {
    const dataset = ctx.dataset()
    const settings = benchmarkSettings(options)
    const { rows } = loadProgress(progressKey(dataset, settings))
    if (!rows.length) {
      console.warn('[benchmark] nothing saved yet for this dataset and settings')
      return
    }
    const summary = summarize(rows, dataset, benchmarkSteps(settings.zooms))
    downloadCsv(toCsv([...rows, ...summary]), `benchmark_${dataset}_partial.csv`)
    console.log(`[benchmark] downloaded ${rows.length} rows`)
  }

  const commands = { benchmarkZoom, benchmarkAll, benchmarkCsv }

  return {
    install() {
      Object.assign(window, commands)
    },
    uninstall() {
      for (const [name, fn] of Object.entries(commands)) {
        if (window[name] === fn) delete window[name]
      }
    }
  }
}
