<template>
  <div class="map-wrapper">
    <div class="map-view">
      <MapControls
        :metadata="metadata"
        :category="selectedCategory"
        :mode="selectedMode"
        :source="selectedSource"
        :palette="selectedPalette"
        :compare-mode="isCompareMode"
        @apply="handleSelection"
        @compare="handleCompareClick"
        @exit-compare="handleExitCompareClick"
        @update:palette="selectedPalette = $event"
        @update:source="selectedSource = $event"
      />
      <div :id="containerId" class="map-container"></div>

      <div class="overlay-stack">
        <DatasetMetadata :metadata="metadata" />
        <div class="legend-stack">
          <PaletteLegend
            :palette="selectedPalette"
            :selected-palette="selectedPalette"
            @update="selectedPalette = $event"
          />
        </div>
      </div>

      <div v-if="tileError" class="tile-error">
        <span>{{ tileError }}</span>
        <button class="tile-error-close" @click="tileError = null" aria-label="Dismiss">✕</button>
      </div>
    </div>

    <div v-if="hoverInfo" class="hover-tooltip"
      :style="{ left: mousePos.x + 12 + 'px', top: mousePos.y + 12 + 'px' }">
      <div><b>Layer:</b> {{ hoverInfo.layer }}</div>
      <div><b>Value:</b> {{ hoverInfo.value }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import MapControls from './MapControls.vue'
import maplibregl from 'maplibre-gl';
import { PMTiles } from 'pmtiles';
import 'maplibre-gl/dist/maplibre-gl.css';
import { palettes } from '../config/palettes.js';
import PaletteLegend from './PaletteLegend.vue';
import { categories } from '../config/categories.js'
import { modes } from '../config/modes.js'
import { regionCountries } from '../config/sources.js'
import { useDatasetsStore } from '../stores/datasets.js'
import { useThemeStore } from '../stores/theme.js';
import DatasetMetadata from './DatasetInfo.vue'
import { startTiming, logSwitchRendered, createBenchmark } from '../utils/renderTiming.js'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const props = defineProps({
  mapId: { type: String, default: () => `map-${Math.random().toString(36).slice(2, 9)}` },
  category: { type: String, default: null },
  mode: { type: String, default: null },
  source: { type: String, default: null },
  palette: { type: String, default: 'classic' },
  compareMode: { type: Boolean, default: false }
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

const theme = useThemeStore()
const datasetsStore = useDatasetsStore()

const containerId = computed(() => `map-container-${props.mapId}`)

const selectedCategory = ref(props.category ?? categories[2].key)
const selectedMode = ref(props.mode ?? modes[2].key)
const selectedSource = ref(props.source ?? null)
const selectedPalette = ref(props.palette ?? 'classic'); 
const compareState = ref(null)
const isCompareMode = computed(() => props.compareMode)
const metadata = ref(null)
const isUpdatingMetadata = ref(false)

const SOURCE_ID = "active-source"
const LAYER_ID = "active-layer"

const isMapReady = ref(false)

watch(() => props.source, (val) => { if (val != null) selectedSource.value = val })
watch(() => props.category, (val) => { if (val != null) selectedCategory.value = val })
watch(() => props.mode, (val) => { if (val != null) selectedMode.value = val })
watch(() => props.palette, (val) => { if (val != null) selectedPalette.value = val })

const layer = computed(() => {
  return `${selectedCategory.value}_${selectedMode.value}`
})

const expanded = ref(false);

// shallowRef: Vue must not proxy maplibre internals (frozen objects break deep proxies)
const map = shallowRef(null);
const hoverInfo = ref(null);

const mousePos = ref({ x: 0, y: 0 });

const selectedSourceInfo = computed(() =>
  datasetsStore.sources.find(s => s.key === selectedSource.value)
)

async function loadMetadata(sourceKey) {
  const src = datasetsStore.sources.find(s => s.key === sourceKey)

  if (!src) {
    metadata.value = null
    return
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}/tiles/${src.region}/${src.key}/metadata.json`
    )
    
    if (!response.ok) {
      throw new Error(`Failed to load metadata (${response.status})`)
    }

    metadata.value = await response.json()

    const availableCategories = metadata.value.categories || []
    const availableModes = metadata.value.modes || []

    selectedCategory.value = availableCategories.includes(selectedCategory.value)
      ? selectedCategory.value
      : availableCategories[0] || null
    
    selectedMode.value = availableModes.includes(selectedMode.value)
      ? selectedMode.value
      : availableModes[0] || null

      console.log("Selected category and mode after loading metadata:", {
        category: selectedCategory.value,
        mode: selectedMode.value
      })
  } catch (err) {
    console.error(err)
    metadata.value = null
  }
}

function handleSelection({ category, mode, source, palette }) {
  selectedCategory.value = category
  selectedMode.value = mode
  selectedSource.value = source
  selectedPalette.value = palette
}

function handleCompareClick(payload) {
  compareState.value = payload

  selectedCategory.value = payload.category
  selectedMode.value = payload.mode
  selectedSource.value = payload.source
  selectedPalette.value = payload.palette

  emit('compare', payload)
}

function handleExitCompareClick(payload) {
  compareState.value = null

  selectedCategory.value = payload.category
  selectedMode.value = payload.mode
  selectedSource.value = payload.source
  selectedPalette.value = payload.palette

  emit('exit-compare', payload)
}

// Background highlight follows the selected source's region
const countryFillColor = computed(() => {
  const countries = regionCountries[selectedSourceInfo.value?.region] ?? []
  const color = palettes[selectedPalette.value]?.colors[0]

  if (!countries.length || !color) return "#00000000"

  return ["match", ["get", "name"], countries, color, "#00000000"]
})

function updateCountryFill() {
  if (!map.value?.getLayer("countries-fill")) return

  map.value.setPaintProperty("countries-fill", "fill-color", countryFillColor.value)
  map.value.setPaintProperty("countries-fill", "fill-opacity", 1)
}

watch(selectedPalette, (newPalette) => {
  if (!map.value || !map.value.getLayer(LAYER_ID)) return

  updateCountryFill()

  const colors = palettes[newPalette]?.colors || []
  const stops = [0, 5, 10, 20, 30]

  map.value.setPaintProperty(LAYER_ID, "fill-color", [
    "interpolate",
    ["linear"],
    ["get", "value"],
    stops[0], colors[0],
    stops[1], colors[1],
    stops[2], colors[2],
    stops[3], colors[3],
    stops[4], colors[4]
  ])
})

function pmtilesUrlFor(layerName) {
  const source = selectedSourceInfo.value
  if (!source) return ''
  return `${API_BASE_URL}/tiles/${source.region}/${source.key}/${source.region}_${layerName}.pmtiles`
}

const pmtilesUrl = computed(() => pmtilesUrlFor(layer.value))

const sourceUrl = computed(() =>
  pmtilesUrl.value ? `pmtiles://${pmtilesUrl.value}` : ''
)

let fittedRegion = selectedSourceInfo.value?.region ?? null
const tileError = ref(null)

async function fitToSourceBounds() {
  const region = selectedSourceInfo.value?.region
  if (!map.value || !pmtilesUrl.value || !region || region === fittedRegion) return

  try {
    const header = await new PMTiles(pmtilesUrl.value).getHeader()
    map.value.fitBounds(
      [[header.minLon, header.minLat], [header.maxLon, header.maxLat]],
      { padding: 20, duration: 0 }
    )
    fittedRegion = region
    tileError.value = null
  } catch (err) {
    console.error(`Could not read PMTiles bounds for ${pmtilesUrl.value}`, err)
    tileError.value = `Tiles for ${layer.value} are not available for this dataset yet.`
  }
}

watch(
  [selectedSource, selectedCategory, selectedMode],
  async () => {
    if (!isMapReady.value) return

    // Time from selection change to hexagons visible on the map
    const timingId = startTiming()
    const start = performance.now()

    await loadMetadata(selectedSource.value)
    const metadataMs = performance.now() - start

    await applyLayer(sourceUrl.value)

    logSwitchRendered(map.value, {
      timingId,
      label: `${selectedSourceInfo.value?.key} / ${layer.value}`,
      start,
      metadataMs
    })
  }
)

watch(
  () => theme.dark,
  (dark) => {
    if (!map.value) return

    map.value.setStyle(
       dark ? 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json' : 'https://tiles.openfreemap.org/styles/liberty',
    );

    map.value.once("styledata", () => {
      setTimeout(() => {
        addCustomLayers();
      }, 0);
    });
  }
)

onMounted(() => {
  datasetsStore.load().then(() => {
    if (!selectedSource.value) {
      const defaultSource = datasetsStore.sources.find(
        s => s.region === 'germany' && s.kernel === 'gaussian'
      )

      selectedSource.value = defaultSource?.key ?? datasetsStore.sources[0]?.key ?? null
    }

    loadMetadata(selectedSource.value)
  })

  if (document.readyState === 'complete') initMap()
  else window.addEventListener('load', initMap, { once: true })
});

function initMap() {
  map.value = new maplibregl.Map({
    container: containerId.value,
    style: theme.dark ? 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json' : 'https://tiles.openfreemap.org/styles/liberty',
    center: [10.4097, 51.4938],
    zoom: 5.3
  });

  map.value.on('load', () => {
    isMapReady.value = true
    addCustomLayers();

    map.value.setLayoutProperty("landcover_wood", "visibility", "none");
    map.value.setLayoutProperty("landcover_grass", "visibility", "none");
    map.value.setLayoutProperty("park", "visibility", "none");
    map.value.setLayoutProperty("park_outline", "visibility", "none");
    map.value.setLayoutProperty("landuse_residential", "visibility", "none");
    map.value.setLayoutProperty("landcover_sand", "visibility", "none");
    
    });


  map.value.on("mousemove", (e) => {
    const zoom = map.value.getZoom();
    mousePos.value = e.point;

    if (zoom <= 10) {
      hoverInfo.value = null;
      map.value.getCanvas().style.cursor = "";
      return;
    }

    const features = map.value.queryRenderedFeatures(e.point, {
      layers: [LAYER_ID]
    });

    const feature = features[0];

    if (feature) {
      map.value.getCanvas().style.cursor = "pointer";

      hoverInfo.value = {
        layer: layer.value,
        value: feature.properties.value
      };
    } else {
      map.value.getCanvas().style.cursor = "";

      hoverInfo.value = {
        layer: layer.value,
        value: 0
      };
    }
  });

  // Print center and zoom values
  map.value.on('moveend', () => {
    const center = map.value.getCenter();
    const zoom = map.value.getZoom();
    console.log(
      `center: [${center.lng.toFixed(4)}, ${center.lat.toFixed(4)}], zoom: ${zoom.toFixed(2)}`
    );
  });

  benchmark.install()
}

onBeforeUnmount(() => {
  window.removeEventListener('load', initMap)
  benchmark.uninstall()
  map.value?.remove()
})

// Console benchmarks (see utils/renderTiming.js)
const benchmark = createBenchmark({
  map: () => map.value,
  dataset: () => (isMapReady.value ? selectedSourceInfo.value?.key ?? null : null),
  metadata: () => metadata.value,
  currentCombo: () => ({ category: selectedCategory.value, mode: selectedMode.value }),
  tileUrl: pmtilesUrlFor,
  showLayer: (layerName) => {
    removeHexLayer()
    map.value.addSource(SOURCE_ID, { type: "vector", url: `pmtiles://${pmtilesUrlFor(layerName)}` })
    setLayer(layerName)
  },
  hideLayer: removeHexLayer,
  restoreLayer: () => {
    setSource()
    setLayer(layer.value)
  }
})

function removeHexLayer() {
  if (map.value.getLayer(LAYER_ID)) map.value.removeLayer(LAYER_ID)
  if (map.value.getSource(SOURCE_ID)) map.value.removeSource(SOURCE_ID)
}


function setSource(layerName) {
  if (!map.value) return

  removeHexLayer()

  map.value.addSource(SOURCE_ID, {
    type: "vector",
    url: sourceUrl.value
  })
}

function setLayer(layerName) {
  const colors = palettes[selectedPalette.value]?.colors ?? []
  const stops = [0, 2, 5, 10, 30]

  const firstSymbolLayer = getFirstSymbolLayerId();

  map.value.addLayer({
    id: LAYER_ID,
    type: "fill",
    source: SOURCE_ID,
    "source-layer": layerName,
    paint: {
      "fill-color": [
        "interpolate",
        ["linear"],
        ["get", "value"],
        stops[0], colors[0],
        stops[1], colors[1],
        stops[2], colors[2],
        stops[3], colors[3],
        stops[4], colors[4]
      ],
      "fill-opacity": 0.8
    }
  }, firstSymbolLayer);
}

function applyLayer(layerName) {
  setSource(layerName)
  setLayer(layer.value)
  const fitted = fitToSourceBounds()
  updateCountryFill()
  return fitted
}

function getFirstSymbolLayerId() {
  return map.value
    .getStyle()
    .layers.find(l => l.type === "symbol")?.id
}

function addCustomLayers() {
  const m = map.value;
  if (!m) return;

  if (!m.getSource("countries")) {
    m.addSource("countries", {
      type: "geojson",
      data: "/countries.geojson"
    });
  }

  const firstSymbolLayer = getFirstSymbolLayerId();

  map.value.addLayer({
      id: "countries-fill",
      type: "fill",
      source: "countries",
      paint: {
        "fill-color": countryFillColor.value,
        "fill-opacity": 1
      }
    }, firstSymbolLayer);

    applyLayer(layer.value);
  }

  
</script>
<style>
.map-wrapper {
  height: 100%;
  width: 100%;
  min-height: 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
  position: relative;
}

.debug {
  padding: 0.5rem;
}

.map-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.map-container {
  flex: 1;
  min-height: 0;
}

.overlay-stack {
  position: absolute;
  width: 12.5rem;
  left: 1.25rem;
  bottom: 1.25rem;

  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-start;
}

.overlay-stack > * {
  width: 100%;
}

.legend-stack {
  display: flex;
  flex-direction: column-reverse;
}

.palette-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tile-error {
  position: absolute;
  top: 5rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #b3261eCC;
  color: white;
  padding: 0.375rem 0.5rem 0.375rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  white-space: nowrap;
  z-index: 1000;
}

.tile-error-close {
  background: none;
  border: none;
  color: inherit;
  font-size: 0.8125rem;
  line-height: 1;
  padding: 0.125rem 0.25rem;
  cursor: pointer;
  opacity: 0.85;
}

.tile-error-close:hover {
  opacity: 1;
}

.hover-tooltip {
  position: absolute;
  background: #000000CC;
  color: white;
  padding: 0.375rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  pointer-events: none;
  white-space: nowrap;
  transform: translate(0, 0);
  transition: left 0.05s linear, top 0.05s linear;
}

.maplibregl-ctrl-attrib.maplibregl-compact {
  background-color: var(--bg);
  color: var(--text);
}

.maplibregl-ctrl-attrib a {
  color: var(--text);
}
</style>