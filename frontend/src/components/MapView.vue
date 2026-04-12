<template>
  <div id="map-container"></div>
</template>

<script setup>
import { onMounted } from 'vue';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

onMounted(() => {
  const map = new maplibregl.Map({
    container: 'map-container',
    style: 'https://demotiles.maplibre.org/style.json',
    center: [10.4515, 51.1657],
    zoom: 5.5
  });

 
 
});
</script>

<style scoped>
#map-container {
  width: 100vw;
  height: 100vh;
}
</style>