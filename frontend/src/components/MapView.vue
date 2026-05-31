<template>
  <div class="app">
    <div id="map-container"></div>

    <div class="legend-stack">

      <PaletteLegend
        :palette="selectedPalette"
        :selected-palette="selectedPalette"
        @update="selectedPalette = $event"
      />

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
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { palettes } from '../config/palettes';
import PaletteLegend from './PaletteLegend.vue';
import SettingsToolbar from './SettingsToolbar.vue';


const selectedPalette = ref('classic'); 
const expanded = ref(false);

const map = ref(null);
const hoverInfo = ref(null);

const mousePos = ref({ x: 0, y: 0 });

watch(selectedPalette, (newPalette) => {
  if (!map.value) return;

  const colors = palettes[newPalette]?.colors || [];

  const stops = [0, 5, 10, 20, 30];

  map.value.setPaintProperty(
    'germany-hospital-layer',
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

onMounted(() => {
  map.value = new maplibregl.Map({
    container: 'map-container',
    style: 'https://demotiles.maplibre.org/style.json',
    center: [10.4097, 51.4938],/*[10.4515, 51.1657]*/
    zoom: 5.7 /*5.5*/
  });

  map.value.on('load', () => {

    // Change Germany's color specifically
    
    
    map.value.setPaintProperty('countries-fill', 'fill-color', [
      'match',
      ['get', 'ADM0_A3'],
      'DEU', palettes[selectedPalette.value].colors[0],  
      '#e0e0e0' 
    ]);
    

    /*
    map.setPaintProperty('countries-fill', 'fill-opacity', 1);

    // Add Bundesländer borders and labels
    map.addSource('bundeslaender', {
      type: 'geojson',
      data: 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/1_sehr_hoch.geo.json'
    });

    map.addLayer({
      id: 'hamburg-border',
      type: 'line',
      source: 'bundeslaender',
      filter: ['==', ['get', 'name'], 'Hamburg'],
      paint: {
        'line-color': '#0000ff',
        'line-width': 2
      }
    })
    */
    // ADD TILES !!!!!!!!!!!!!
      console.log("🟢 Map loaded");

      map.value.addSource("germany-hospital", {
        type: "vector",
        url: "pmtiles://http://localhost:8000/tiles/germany_hospital_bike.pmtiles" //"pmtiles://http://localhost:8000/tiles/hamburg_hospital_drive.pmtiles"
      });

      console.log("📦 Source added: supermarket");

      map.value.on("sourcedata", (e) => {
        if (e.sourceId === "supermarket") {
          console.log("📡 Supermarket source event:", e);

          if (e.isSourceLoaded) {
            console.log("✅ Supermarket source fully loaded");
          }
        }
      });

      const colors = palettes[selectedPalette.value]?.colors ?? [];
      const stops = [0, 2, 5, 10, 30];

      map.value.addLayer({
      id: "germany-hospital-layer",
      //type: "circle",
      type: "fill",
      source: "germany-hospital",
      "source-layer": "hospital_bike", // Adjust this to match the actual layer name in your PMTiles
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
      }, "countries-label" // Place the supermarket layer below country labels
      );

      console.log("🎨 Layer added: germany-hospital-layer");
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
      layers: ["germany-hospital-layer"]
    });

    const feature = features[0];

    if (feature) {
      map.value.getCanvas().style.cursor = "pointer";

      hoverInfo.value = {
        layer: "hospital_drive",
        value: feature.properties.value
      };
    } else {
      map.value.getCanvas().style.cursor = "";

      hoverInfo.value = {
        layer: "hospital_drive",
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
</script>
<style>
.app {
  position: relative;
  width: 100vw;
  height: 100vh;
}

#map-container {
  position: absolute;
  inset: 0;
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

