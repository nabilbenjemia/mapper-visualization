import { createApp } from 'vue';
import './style.css';
import App from './App.vue';
import maplibregl from 'maplibre-gl';
import * as pmtiles from "pmtiles";

const protocol = new pmtiles.Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);

createApp(App).mount('#app')
