<script setup>
import Header from './components/Header.vue';
import MapViewContainer from './components/MapViewContainer.vue';
</script>

<template>
  <div class="app">
    <Header class="app-header" />
    <main class="app-main">
      <MapViewContainer />
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.app-header {
  position: relative !important;
  z-index: 2;
}

.app-main {
  flex: 1;
  min-height: 0; 
  display: flex;
  flex-direction: column;
}

.app-main > .map-wrapper {
  flex: 1;
  min-height: 0;
}

.map-wrapper .map-view,
.map-wrapper #map-container {
  height: 100%;
  width: 100%;
}
</style>