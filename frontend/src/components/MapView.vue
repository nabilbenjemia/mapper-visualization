<template>
  <div class="map-wrapper">
    <div class="map-view">

      <MapControls
        :category="selectedCategory"
        :mode="selectedMode"
        @apply="handleSelection"
      />
      <div id="map-container"></div>

      <div class="legend-stack">
        <PaletteLegend
          :palette="selectedPalette"
          :selected-palette="selectedPalette"
          @update="selectedPalette = $event"
        />
      </div>
    </div>

    <div
      v-if="hoverInfo"
      class="hover-tooltip"
      :style="{
        left: mousePos.x + 12 + 'px',
        top: mousePos.y + 12 + 'px'
      }"
    >
      <div><b>Layer:</b> {{ hoverInfo.layer }}</div>
      <div><b>Value:</b> {{ hoverInfo.value }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import MapControls from './MapControls.vue'
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { palettes } from '../config/palettes';
import PaletteLegend from './PaletteLegend.vue';
import SettingsToolbar from './SettingsToolbar.vue';
import { categories } from '../config/categories'
import { modes } from '../config/modes'

//////////////////////////////////////////
const selectedCategory = ref(categories[2].key)
const selectedMode = ref(modes[2].key)

const layer = computed(() => {
  return `${selectedCategory.value}_${selectedMode.value}`
})
/////////////////////////////////////////
const SOURCE_ID = "active-source"
const LAYER_ID = "active-layer"

const selectedPalette = ref('classic'); 
const expanded = ref(false);

const map = ref(null);
const hoverInfo = ref(null);

const mousePos = ref({ x: 0, y: 0 });

function handleSelection({ category, mode }) {
  selectedCategory.value = category
  selectedMode.value = mode
}

watch(selectedPalette, (newPalette) => {
  if (!map.value) return;

  const colors = palettes[newPalette]?.colors || [];

  const stops = [0, 5, 10, 20, 30];

  map.value.setPaintProperty(
    LAYER_ID,
    'fill-color',
    [
      'interpolate',
      ['linear'],
      ['get', 'value'],
      stops[0], colors[0],
      stops[1], colors[1],
      stops[2], colors[2],
      stops[3], colors[3],
      stops[4], colors[4]
    ]
  );

  map.value.setPaintProperty('countries-fill', 'fill-color', [
      'match',
      ['get', 'ADM0_A3'],
      'DEU', palettes[selectedPalette.value].colors[0],   
      '#e0e0e0' 
    ]);
});

watch(layer, (newLayer) => {
  applyLayer(newLayer)
})

onMounted(() => {
  map.value = new maplibregl.Map({
    container: 'map-container',
    style: 'https://demotiles.maplibre.org/style.json',
    center: [10.4097, 51.4938],/*[10.4515, 51.1657]*/
    zoom: 5.7 /*5.5*/
  });

  map.value.on('load', () => {

    map.value.setPaintProperty('countries-fill', 'fill-color', [
      'match',
      ['get', 'ADM0_A3'],
      'DEU', palettes[selectedPalette.value].colors[0],  
      '#e0e0e0' 
    ]);
    
    applyLayer(layer.value)
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


function applyLayer(layerName) {
  if (!map.value) return

  if (map.value.getLayer(LAYER_ID)) {
    map.value.removeLayer(LAYER_ID)
  }

  if (map.value.getSource(SOURCE_ID)) {
    map.value.removeSource(SOURCE_ID)
  }

  map.value.addSource(SOURCE_ID, {
    type: "vector",
    url: `pmtiles://http://localhost:8000/tiles/germany_${layerName}.pmtiles`
  })

  const colors = palettes[selectedPalette.value]?.colors ?? []
  const stops = [0, 2, 5, 10, 30]

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
  }, "countries-label")
}

</script>
<style>
.map-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.debug {
  padding: 8px;
}

.map-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

#map-container {
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
</style>

