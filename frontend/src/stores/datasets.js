import { defineStore } from 'pinia'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

function capitalize(word) {
  return word.charAt(0).toUpperCase() + word.slice(1)
}

export const useDatasetsStore = defineStore('datasets', {
  state: () => ({
    sources: [],
    loaded: false,
    error: null,
  }),
  actions: {
    async load() {
      if (this.loaded) return

      try {
        const response = await fetch(`${API_BASE_URL}/datasets`)

        if (!response.ok) {
          throw new Error(`Failed to load datasets (${response.status})`)
        }

        const datasets = await response.json()

        this.sources = datasets.map(d => ({
          key: d.key,
          region: d.region,
          kernel: d.kernel,
          label: `${capitalize(d.region)} (${capitalize(d.kernel)})`,
        }))
        this.loaded = true
      } catch (err) {
        console.error(err)
        this.error = err
      }
    },
  },
})
