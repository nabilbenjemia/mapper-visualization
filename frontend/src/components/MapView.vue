<template>
  <div id="map-container" class="w-screen h-screen"></div>
</template>

<script setup>
import { onMounted } from 'vue';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

onMounted(() => {
  const map = new maplibregl.Map({
    container: 'map-container',
    style: 'https://demotiles.maplibre.org/style.json',
    center: [10.4097, 51.4938],/*[10.4515, 51.1657]*/
    zoom: 5.7 /*5.5*/
  });

  map.on('load', () => {

    // Change Germany's color specifically
    /*
    map.setPaintProperty('countries-fill', 'fill-color', [
      'match',
      ['get', 'ADM0_A3'],
      'DEU', '#ff0000',      // Change this to your desired color (e.g., Red)
      '#d1d1d1'             // This is the color for the REST of the world
    ]);
    
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

      map.addSource("hospital", {
        type: "vector",
        url: "pmtiles://http://localhost:8000/tiles/hamburg_hospital_drive.pmtiles"
      });

      console.log("📦 Source added: hospital");

      map.on("sourcedata", (e) => {
        if (e.sourceId === "hospital") {
          console.log("📡 Hospital source event:", e);

          if (e.isSourceLoaded) {
            console.log("✅ Hospital source fully loaded");
          }
        }
      });

      map.addLayer({
        id: "hospital-layer",
        type: "fill", //"circle",
        source: "hospital",
        "source-layer": "hospital_drive",
        paint: {
          "fill-color": [
            'interpolate',
            ['linear'],
            ['get', 'value'],
            0,   "#2c7bb6",   // blue
            5,   "#abd9e9",
            10,  "#ffffbf",
            20,  "#fdae61",
            30,  "#d7191c"    // red
          ]
        }
      });

      console.log("🎨 Layer added: hospital-layer");
    });

  // Print center and zoom values
  map.on('moveend', () => {
    const center = map.getCenter();
    const zoom = map.getZoom();
    console.log(
      `center: [${center.lng.toFixed(4)}, ${center.lat.toFixed(4)}], zoom: ${zoom.toFixed(2)}`
    );
  });
});
</script>

