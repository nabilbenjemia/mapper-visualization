<template>
  <div class="map-wrapper">
    <div class="map-view">
      <MapControls
        :category="selectedCategory"
        :mode="selectedMode"
        :palette="selectedPalette"
        :compare-mode="isCompareMode"
        @apply="handleSelection"
        @compare="handleCompareClick"
        @exit-compare="handleExitCompareClick"
        @update:palette="selectedPalette = $event"
      />
      <div :id="containerId" class="map-container"></div>

      <div class="legend-stack">
        <PaletteLegend
          :palette="selectedPalette"
          :selected-palette="selectedPalette"
          @update="selectedPalette = $event"
        />
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
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import MapControls from './MapControls.vue'
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { palettes } from '../config/palettes.js';
import PaletteLegend from './PaletteLegend.vue';
import { categories } from '../config/categories.js'
import { modes } from '../config/modes.js'
import { useThemeStore } from '../stores/theme.js';

const props = defineProps({
  mapId: { type: String, default: () => `map-${Math.random().toString(36).slice(2, 9)}` },
  category: { type: String, default: null },
  mode: { type: String, default: null },
  palette: { type: String, default: 'classic' },
  compareMode: { type: Boolean, default: false }
})

const emit = defineEmits([
  'update:category',
  'update:mode',
  'update:palette',
  'apply',
  'compare',
  'exit-compare'
])

const theme = useThemeStore()

const containerId = computed(() => `map-container-${props.mapId}`)

const selectedCategory = ref(props.category ?? categories[2].key)
const selectedMode = ref(props.mode ?? modes[2].key)
const selectedPalette = ref(props.palette ?? 'classic'); 
const compareState = ref(null)
const isCompareMode = computed(() => props.compareMode)

const SOURCE_ID = "active-source"
const LAYER_ID = "active-layer"

const isMapReady = ref(false)

watch(() => props.category, (val) => { if (val != null) selectedCategory.value = val })
watch(() => props.mode, (val) => { if (val != null) selectedMode.value = val })
watch(() => props.palette, (val) => { if (val != null) selectedPalette.value = val })

const layer = computed(() => {
  return `${selectedCategory.value}_${selectedMode.value}`
})

const expanded = ref(false);

const map = ref(null);
const hoverInfo = ref(null);

const mousePos = ref({ x: 0, y: 0 });

function handleSelection({ category, mode, palette }) {
  selectedCategory.value = category
  selectedMode.value = mode
  selectedPalette.value = palette
}

function handleCompareClick(payload) {
  compareState.value = payload

  selectedCategory.value = payload.category
  selectedMode.value = payload.mode
  selectedPalette.value = payload.palette

  emit('compare', payload)
}

function handleExitCompareClick(payload) {
  compareState.value = null

  selectedCategory.value = payload.category
  selectedMode.value = payload.mode
  selectedPalette.value = payload.palette

  emit('exit-compare', payload)
}

watch(selectedPalette, (newPalette) => {
  if (!map.value || !map.value.getLayer(LAYER_ID)) return
  
  map.value.setPaintProperty(
    "countries-fill",
    "fill-color",
    [
      "case",
      ["==", ["get", "name"], "Germany"],
      palettes[selectedPalette.value].colors[0],
      "#00000000"
    ]
  )
  
  
  map.value.setPaintProperty(
    "countries-fill",
    "fill-opacity",
    1
  )

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

watch(layer, (val) => {
  if (!isMapReady.value) return
  if (!val) return
  applyLayer(val)
})

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
  map.value = new maplibregl.Map({
    container: containerId.value,
    style: theme.dark ? 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json' : 'https://tiles.openfreemap.org/styles/liberty',
    center: [10.4097, 51.4938],/*[10.4515, 51.1657]*/
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
});

onBeforeUnmount(() => {
  map.value?.remove() 
})

const sourceUrl = computed(() =>
  `pmtiles://http://localhost:8000/tiles/germany_${layer.value}.pmtiles`
)

function setSource(layerName) {
  if (!map.value) return

  if (map.value.getLayer(LAYER_ID)) {
    map.value.removeLayer(LAYER_ID)
  }

  if (map.value.getSource(SOURCE_ID)) {
    map.value.removeSource(SOURCE_ID)
  }

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
  setLayer(layerName)
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
        "fill-color": [
          "match",
          ["get", "name"],
          "Germany",
          palettes[selectedPalette.value].colors[0],
          "#00000000"
        ],
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
  padding: 8px;
}

.map-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.map-container {
  flex: 1;
  min-height: 0; /* critical */
}

.legend-stack {
  position: absolute;
  bottom: 20px;
  left: 20px;

  display: flex;
  flex-direction: column-reverse;
  gap: 8px;

  overflow: visible;
}

.palette-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.hover-tooltip {
  position: absolute;
  background: #000000CC;
  color: white;
  padding: 6px 8px;
  border-radius: 6px;
  font-size: 12px;
  pointer-events: none;
  white-space: nowrap;
  transform: translate(0, 0);
  transition: left 0.05s linear, top 0.05s linear;
}

.maplibregl-ctrl-attrib.maplibregl-compact {
  background-color: var(--bg);
  color: var(--text);
}

.maplibregl-ctrl-attrib a{
  color: var(--text);
}


</style>

