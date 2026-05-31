<template>
  <div class="settings-toolbar">
    <PaletteLegend
      v-for="(palette, key) in palettes"
      :key="key"
      :palette="key"
      :selected="selectedPalette === key"
      compact
      @click="selectPalette(key)"
    />
  </div>
</template>

<script setup>
import PaletteLegend from './PaletteLegend.vue';
import { palettes } from '../config/palettes';

const props = defineProps({
  selectedPalette: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['update:selectedPalette']);

function selectPalette(key) {
  emit('update:selectedPalette', key);
}
</script>

<style scoped>
.settings-toolbar {
  position: absolute;
  top: 60px;
  right: 20px;

  z-index: 1000;

  display: flex;
  flex-direction: column;
  gap: 12px;

  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;

  padding: 12px;

  box-shadow:
    0 4px 12px rgba(0,0,0,0.08),
    0 2px 4px rgba(0,0,0,0.04);
}
</style>