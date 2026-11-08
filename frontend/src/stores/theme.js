import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    dark: false
  }),
  actions: {
    toggle() {
    this.dark = !this.dark

    document.body.classList.toggle('dark', this.dark)
    }
  }
})

