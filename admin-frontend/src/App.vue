<script setup>
import { ref } from 'vue';
import Header from './components/Header.vue';
import DatasetView from './components/DatasetView.vue';

const homeKey = ref(0);
function goHome() {
  homeKey.value += 1; 
}
</script>

<template>
  <div class="app">
    <Header class="app-header" @go-home="goHome"/>
    <main class="app-main">
      <DatasetView></DatasetView>
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
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  position: relative !important;
  z-index: 2;
}

.app-main {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
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