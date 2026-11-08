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
  top: 3.75rem;
  right: 1.25rem;

  z-index: 1000;

  display: flex;
  flex-direction: column;
  gap: 0.75rem;

  background: white;
  border: 0.0625rem solid #e5e7eb;
  border-radius: 1rem;

  padding: 0.75rem;

  box-shadow:
    0 0.25rem 0.75rem rgba(0,0,0,0.08),
    0 0.125rem 0.25rem rgba(0,0,0,0.04);
}
</style>