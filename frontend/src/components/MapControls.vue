<template>
    <div class="controls">
      <div class="select-wrapper">
        <select v-model="selectedCategory">
          <option
            v-for="c in categories"
            :key="c.key"
            :value="c.key"
          >
            {{ c.label }}
          </option>
        </select>
        <span class="chevron" aria-hidden>▾</span>
      </div>

      <div class="select-wrapper">
        <select v-model="selectedMode">
          <option
            v-for="m in modes"
            :key="m.key"
            :value="m.key"
          >
            {{ m.label }}
          </option>
        </select>
        <span class="chevron" aria-hidden>▾</span>
      </div>

      <button class="ok-button" @click="loadTiles">
        Select
      </button>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { categories } from '../config/categories'
import { modes } from '../config/modes'

const selectedCategory = ref(categories[0].key)
const selectedMode = ref(modes[0].key)

const emit = defineEmits(['apply'])

function loadTiles() {
  console.log('Applying selection:', selectedCategory.value, selectedMode.value)
  emit('apply', {
    category: selectedCategory.value,
    mode: selectedMode.value
  })
}
</script>

<style>
/* centered near the top, larger and nicer controls */
.controls {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  margin-top: 10px;

  display: flex;
  gap: 10px;
  align-items: center;

  background: rgba(255,255,255,0.95);
  padding: 10px 14px;
  border-radius: 10px;
  box-shadow: 0 6px 18px rgba(12,18,30,0.14);
  border: 1px solid rgba(0,0,0,0.06);
  backdrop-filter: blur(6px);
  font-size: 15px;
  min-width: 360px;
}

/* wrapper so we can show a custom chevron */
.select-wrapper {
  position: relative;
  min-width: 130px;
}

/* selects */
.select-wrapper select,
.controls select {
  appearance: none;
  -webkit-appearance: none;
  padding: 8px 32px;
  padding-right: 44px; /* increased space for larger chevron */
  border-radius: 8px;
  border: 1px solid #dcdcdc;
  background: #fff;
  font-size: 14px;
  color: #222;
  min-width: 130px;
  cursor: pointer;
  max-height: 50px;
}

/* chevron indicator */
.select-wrapper .chevron {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  color: #333;
  font-size: 18px; /* larger */
  line-height: 1;
  user-select: none;
  opacity: 1; /* fully visible */
  text-shadow: 0 1px 0 rgba(255,255,255,0.6);
}


/* primary OK button */
.ok-button {
  padding: 8px 14px;
  border-radius: 8px;
  border: none;
  background: #1976d2;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 6px 12px rgba(25,118,210,0.18);
  transition: transform 0.08s ease, box-shadow 0.12s ease;
}

.ok-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(25,118,210,0.2);
}

.ok-button:active {
  transform: translateY(0);
  box-shadow: 0 6px 12px rgba(25,118,210,0.16);
}
</style>