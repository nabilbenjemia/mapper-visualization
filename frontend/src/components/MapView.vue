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
      id: 'bundeslaender-outline',
      type: 'line',
      source: 'bundeslaender',
      paint: {
        'line-color': '#627BC1',
        'line-width': 1.5
      }
    });

    // Labels from properties.name
    /*
    map.addLayer({
      id: 'bundeslaender-labels',
      type: 'symbol',
      source: 'bundeslaender',
      layout: {
        'text-field': ['get', 'name'],
        'text-size': 12,
        'text-font': ['Open Sans Semibold'],
        'text-allow-overlap': false
      },
      paint: {
        'text-color': '#1f2937',
        'text-halo-color': '#ffffff',
        'text-halo-width': 1.2
      }
    });*/
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

