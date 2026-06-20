<template>
  <div class="map-page">
    <MapView
      v-if="layoutMode === 'single'"
      map-id="single"
      :category="mapA.category"
      :mode="mapA.mode"
      :compare-mode="false"
      @compare="enterCompare"
      @update="val => mapA = val"
    />

    <div v-else class="compare">
      <MapView
        map-id="mapA"
        class="map-pane"
        :style="{ width: `${leftWidth}%` }"
        :category="mapA.category"
        :mode="mapA.mode"
        :compare-mode="true"
        @update="val => mapA = val"
        @exit-compare="exitCompare('A', $event)"
      />
      <div class="compare-divider" 
        @mousedown="startResize"
      />
      <MapView
        map-id="mapB"
        class="map-pane"
        :style="{ width: `${100 - leftWidth}%` }"
        :category="mapB.category"
        :mode="mapB.mode"
        :compare-mode="true"
        @update="val => mapB = val"
        @exit-compare="exitCompare('B', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from 'vue'
import MapView from './MapViewSingle.vue'

const leftWidth = ref(50) 
let isResizing = false

const layoutMode = ref('single')
const mapA = ref({ category: 'hospital', mode: 'drive' })
const mapB = ref({ category: 'default', mode: 'default' })

function enterCompare(payload) {
  mapA.value = payload
  mapB.value = { ...payload }
  layoutMode.value = 'compare'
}

function exitCompare(source, payload) {
  mapA.value = payload
  layoutMode.value = 'single'
}



function startResize(e) {
  isResizing = true
  window.addEventListener('mousemove', resize)
  window.addEventListener('mouseup', stopResize)
}

function resize(e) {
  if (!isResizing) return

  const containerWidth = window.innerWidth
  const percent = (e.clientX / containerWidth) * 100

  // clamp so it doesn't collapse
  leftWidth.value = Math.max(10, Math.min(90, percent))
}

function stopResize() {
  isResizing = false
  window.removeEventListener('mousemove', resize)
  window.removeEventListener('mouseup', stopResize)
}

onBeforeUnmount(() => stopResize())
</script>

<style scoped>
.map-page {
  height: 100vh; 
  width: 100%;
}

.compare {
  height: 100%;
  width: 100%;
  display: flex;
}


.map-pane {
  flex: 0 0 auto;
  min-width: 0;
  height: 100%;
}

.compare-divider { width: 5px; background: white; flex: 0 0 auto; }
.compare-divider:hover { cursor: col-resize; }
</style>