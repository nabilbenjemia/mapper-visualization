<template>
  <div class="legend-container">
    <div class="gradient-wrapper">
  <div class="scale">
    <div class="labels">
      <span>30</span>
      <span>20</span>
      <span>10</span>
      <span>0</span>
    </div>

    <div
      class="gradient-bar"
      :style="gradientStyle"
    />
  </div>
</div>

    <div v-if="expanded" class="palette-list">
      <button
        v-for="(p, key) in palettes"
        :key="key"
        class="palette-option"
        :class="{ active: selectedPalette === key }"
        @click="changePalette(key)"
      >
        <div
          class="palette-preview"
          :style="{
            background: `linear-gradient(to top, ${p.colors.join(',')})`
          }"
        />

        <span>{{ p.name }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { palettes } from '../config/palettes';

const props = defineProps({
  map: Object,
  palette: String,
});


const expanded = ref(false);

const gradientStyle = computed(() => {
  const palette = palettes[props.palette] ?? [];

  const colors = palette.filter((_, i) => i % 2 === 1);

  console.log("Selected palette:", props.palette, "Colors:", colors);
  return {
  background: `linear-gradient(to top, ${palette
    .filter((_, i) => i % 2 === 1)
    .join(",")})`
};
});

function toggleExpanded() {
  expanded.value = !expanded.value;
}

function changePalette(key) {
  emit("update:palette", key);

  const palette = palettes[key];

  props.map.setPaintProperty(
    props.layerId,
    'fill-color',
    [
      'interpolate',
      ['linear'],
      ['get', 'value'],
      0, palette[0],
      1, palette[1],
      5, palette[2],
      10, palette[3],
      20, palette[4],
      30, palette[5]
    ]
  );
}
</script>

<style scoped>

.legend-container {
  position: absolute;
  bottom: 20px;
  left: 20px;

  z-index: 1000;

  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;

  width: 80px;
  padding: 16px;
}

/* wrapper for gradient + labels */
.gradient-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

/* vertical scale layout */
.scale {
  display: flex;
  align-items: stretch;
  gap: 8px;
}

/* numeric labels aligned with bar */
.labels {
  display: flex;
  flex-direction: column;
  justify-content: space-between;

  height: 140px;

  font-size: 12px;
  color: #6b7280;
}

/* gradient bar (VERTICAL) */
.gradient-bar {
  width: 18px;
  height: 140px;

  border-radius: 999px;
  border: 1px solid #d1d5db;
}

/* palette list (expanded section) */
.palette-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* palette option button */
.palette-option {
  display: flex;
  align-items: center;
  gap: 10px;

  border: 1px solid #e5e7eb;
  background: white;

  border-radius: 10px;
  padding: 8px;

  cursor: pointer;
  transition: all 0.2s ease;
}

.palette-option:hover {
  background: #f9fafb;
}

.palette-option.active {
  border-color: #6366f1;
}

/* preview mini gradient */
.palette-preview {
  width: 80px;
  height: 14px;

  border-radius: 999px;
  border: 1px solid #d1d5db;
}

/* optional toggle button (if you re-add it later) */
.toggle-button {
  border: none;
  background: #f3f4f6;

  width: 28px;
  height: 28px;

  border-radius: 8px;
  cursor: pointer;

  font-size: 18px;
}
</style>