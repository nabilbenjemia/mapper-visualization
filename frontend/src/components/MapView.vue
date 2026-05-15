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



watch(selectedPalette, (newPalette) => {
  if (!map.value) return;

  const colors = palettes[newPalette]?.colors || [];

  const stops = [0, 5, 10, 20, 30];

  map.value.setPaintProperty(
    'germany-supermarket-layer',
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

      map.value.addSource("germany-supermarket", {
        type: "vector",
        url: "pmtiles://http://localhost:8000/tiles/germany_supermarket_transit.pmtiles" //"pmtiles://http://localhost:8000/tiles/hamburg_hospital_drive.pmtiles"
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
      const stops = [0, 5, 10, 20, 30];

      map.value.addLayer({
      id: "germany-supermarket-layer",
      //type: "circle",
      type: "fill",
      source: "germany-supermarket",
      "source-layer": "supermarket_transit",
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

      console.log("🎨 Layer added: germany-supermarket-layer");

      //HAMBURG supermarket transit
      /*
      map.addSource("hamburg-supermarket", {
        type: "vector",
        url: "pmtiles://http://localhost:8000/tiles/hamburg_supermarket_transit.pmtiles" //"pmtiles://http://localhost:8000/tiles/hamburg_hospital_drive.pmtiles"
      });

      map.addLayer({
      id: "hamburg-supermarket-layer",
      type: "circle",
      source: "hamburg-supermarket",
      "source-layer": "supermarket_transit",
      paint: {
        "circle-radius": 2.5,
        "circle-color": [
          "interpolate",
          ["linear"],
          ["get", "value"],
          0, "#2c7bb6",
          5, "#abd9e9",
          10, "#ffffbf",
          20, "#fdae61",
          30, "#d7191c"
        ],
        "circle-opacity": 0.8
      }
      });*/
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
</style>

