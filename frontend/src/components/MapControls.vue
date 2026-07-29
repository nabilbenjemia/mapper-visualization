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

      <div class="select-wrapper">
        <select v-model="selectedSource">
          <option
            v-for="c in sources"
            :key="c.key"
            :value="c.key"
          >
            {{ c.label }}
          </option>
        </select>
        <span class="chevron" aria-hidden>▾</span>
      </div>

      <button class="ok-button" @click="loadTiles">
        Select
      </button>
      <button class="compare-button" v-if="!compareMode" @click="compare">Compare</button>
      <button class="compare-button" v-else @click="exitCompare">Exit</button>
    </div>
</template>

<script setup>
import { categories as categoryConfig } from '../config/categories'
import { modes as modeConfig } from '../config/modes'
import { sources } from '../config/sources'
import { watch, computed } from 'vue'
import { ref } from 'vue'

const props = defineProps({
  metadata: Object,
  category: String,
  mode: String,
  source: String,
  palette: String,
  compareMode: Boolean
})

const selectedCategory = ref(props.category)
const selectedMode = ref(props.mode)
const selectedSource = ref(props.source)
const selectedPalette = ref(props.palette)

watch(() => props.category, (v) => {
  if (v != null) selectedCategory.value = v
})

watch(() => props.mode, (v) => {
  if (v != null) selectedMode.value = v
})

watch(() => props.source, (v) => {
  if (v != null) selectedSource.value = v
})

watch(() => props.palette, (v) => {
  if (v != null) selectedPalette.value = v
})

const emit = defineEmits([
  'update:category',
  'update:mode',
  'update:source',
  'update:palette',
  'apply',
  'compare',
  'exit-compare'
])

watch(() => props.category, v => selectedCategory.value = v)
watch(() => props.mode, v => selectedMode.value = v)
watch(() => props.source, v => selectedSource.value = v)
watch(() => props.palette, v => selectedPalette.value = v)
watch(selectedPalette, (v) => emit('update:palette', v) )
watch(selectedSource, (v) => emit('update:source', v))

const categories = computed(() => {
    if (!props.metadata) return []

    return props.metadata.categories
        .map(key => categoryConfig.find(c => c.key === key))
        .filter(Boolean)
})

const modes = computed(() => {
    if (!props.metadata) return []

    return props.metadata.modes
        .map(key => modeConfig.find(m => m.key === key))
        .filter(Boolean)
})

function loadTiles() {
  console.log("Loading tiles with selection:", {
    category: selectedCategory.value,
    mode: selectedMode.value,
    source: selectedSource.value,
    palette: selectedPalette.value
  });
  emit('apply', {
    category: selectedCategory.value,
    mode: selectedMode.value,
    source: selectedSource.value,
    palette: selectedPalette.value
  })
}

function compare() {
  const payload = {
    category: selectedCategory.value,
    mode: selectedMode.value,
    source: selectedSource.value,
    palette: selectedPalette.value
  }

  emit('apply', payload)
  emit('compare', payload)
}

function exitCompare() {
  emit('exit-compare', {
    category: selectedCategory.value,
    mode: selectedMode.value,
    source: selectedSource.value,
    palette: selectedPalette.value
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

  background: var(--bg);
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
  background: var(--bg);
  font-size: 14px;
  color: var(--text);
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

.compare-button {
  padding: 8px 14px;
  border-radius: 8px;
  border: #1976d2 solid 1px;
  font-weight: 600;
  color: #1976d2;
  cursor: pointer;
  box-shadow: 0 6px 12px rgba(85,85,85,0.18);
  transition: transform 0.08s ease, box-shadow 0.12s ease;
}

.compare-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(85,85,85,0.2);
}
</style>