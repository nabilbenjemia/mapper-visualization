<template>
  <div class="legend-stack">

    <!-- SELECTED -->
    <div class="legend-container" @click="toggleExpanded">
      <div
        class="gradient-bar"
        :style="gradientStyle"
      />

      <div class="labels-row">
        <span>0</span>
        <span>10</span>
        <span>20</span>
        <span>30</span>
      </div>
    </div>

    <!-- EXPANDED LIST -->
    <div v-if="expanded" class="palette-list">
      <div
        v-for="[key, p] in otherPalettes"
        :key="key"
        class="palette-option"
        @click="selectPalette(key)"
      >
        <div
          class="palette-preview"
          :style="{
            background: `linear-gradient(to right, ${p.colors.join(',')})`
          }"
        />
      </div>
    </div>

  </div>
</template>



<script setup>
import { computed, ref } from 'vue'
import { palettes } from '../config/palettes'

const props = defineProps({
  selectedPalette: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update'])

const expanded = ref(false)

function toggleExpanded() {
  expanded.value = !expanded.value
}

function selectPalette(key) {
  emit('update', key);
  expanded.value = false;
  console.log(`Selected palette: ${key}`);
}

const gradientStyle = computed(() => {
  const colors = palettes?.[props.selectedPalette]?.colors || []
  return {
    background: `linear-gradient(to right, ${colors.join(', ')})`
  }
})

const paletteEntries = computed(() => {
  return Object.entries(palettes)
})

const otherPalettes = computed(() =>
  Object.entries(palettes).filter(
    ([key]) => key !== props.selectedPalette
  )
)
</script>

<style>
.legend-stack {
  position: absolute;
  bottom: 20px;
  left: 20px;

  display: flex;
  flex-direction: column-reverse;
  gap: 8px;

  overflow: visible;
  z-index: 9999;
}

.legend-container {
  width: 200px;
  padding: 10px;

  border: 1px solid #e5e7eb;
  border-radius: 10px;

  background: var(--bg);
  cursor: pointer;
}

.gradient-bar {
  width: 100%;
  height: 14px;
  border-radius: 999px;
}

.labels-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text);
}

/* each option */
.palette-option {
  width: 200px;
  padding: 14px;
  cursor: pointer;

  border: 1px solid #e5e7eb;
  border-radius: 10px;

  background: var(--bg);
}



.palette-preview {
  width: 100%;
  height: 14px;
  border-radius: 999px;
}
</style>