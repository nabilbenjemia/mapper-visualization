<template>
  <div class="map-page">
    <MapView
      v-if="layoutMode === 'single'"
      map-id="single"
      :category="mapA.category"
      :mode="mapA.mode"
      :source="mapA.source"
      :palette="mapA.palette"
      :compare-mode="false"
      @compare="enterCompare"
      @update="val => mapA = val"
    />

    <div v-else class="compare">
      <MapView
        map-id="mapA"
        class="map-pane"
        :style="{ flexBasis: leftWidth + '%' }"
        :category="mapA.category"
        :mode="mapA.mode"
        :source="mapA.source"
        :palette="mapA.palette"
        :compare-mode="true"
        @update="val => mapA = val"
        @exit-compare="exitCompare('A', $event)"
      />

      <div class="compare-divider" @mousedown="startResize" />

      <MapView
        map-id="mapB"
        class="map-pane"
        :style="{ flexBasis: (100 - leftWidth) + '%' }"
        :category="mapB.category"
        :mode="mapB.mode"
        :source="mapB.source"
        :palette="mapB.palette"
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
let latestX = 0
let rafId = null

const layoutMode = ref('single')

const mapA = ref({
  category: 'hospital',
  mode: 'drive',
  palette: 'classic'
})

const mapB = ref({
  category: 'hospital',
  mode: 'drive',
  palette: 'classic'
})

function enterCompare(payload) {
  console.log('Entering compare mode with payload:', payload)
  mapA.value = payload
  mapB.value = { ...payload }
  layoutMode.value = 'compare'
}

function exitCompare(source, payload) {
  mapA.value = payload
  layoutMode.value = 'single'
}


function startResize() {
  isResizing = true
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', stopResize)
}

function onMove(e) {
  latestX = e.clientX

  if (!rafId) {
    rafId = requestAnimationFrame(updateWidth)
  }
}

function updateWidth() {
  const percent = (latestX / window.innerWidth) * 100
  leftWidth.value = Math.max(10, Math.min(90, percent))

  rafId = null
}

function stopResize() {
  isResizing = false
  window.removeEventListener('mousemove', onMove)
  window.removeEventListener('mouseup', stopResize)

  if (rafId) {
    cancelAnimationFrame(rafId)
    rafId = null
  }
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
  flex-direction: row;
}


.map-pane {
  height: 100%;
  flex-grow: 0;
  flex-shrink: 0;
  min-width: 0;
  overflow: hidden;
}

.compare-divider {
  width: 0.375rem;
  cursor: col-resize;
  background: white;
  z-index: 10;
  user-select: none;
  flex: 0 0 auto;
}

.compare-divider:hover {
  cursor: col-resize;
}
</style>