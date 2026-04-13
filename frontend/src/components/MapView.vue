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
    // 1. Make the SEA/BACKGROUND white (or light grey)
    // 1. Change the Sea (Background)
  if (map.getLayer('background')) {
    map.setPaintProperty('background', 'background-color', '#ffffff');
  } else {
    console.warn('Background layer not found. Please check the layer name in the style.');
  }

  // 2. Change Germany's color specifically
  if (map.getLayer('countries-fill')) {
    map.setPaintProperty('countries-fill', 'fill-color', [
      'match',
      ['get', 'ADM0_A3'],
      'DEU', '#ff0000',      // Change this to your desired color (e.g., Red)
      '#d1d1d1'             // This is the color for the REST of the world
    ]);
    
    map.setPaintProperty('countries-fill', 'fill-opacity', 1);
  } else {
    console.warn('Countries layer not found. Please check the layer name in the style.');
  }

    
  });
});
</script>

