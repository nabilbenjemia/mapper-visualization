import { createApp } from 'vue';
import {createPinia} from 'pinia';
import './style.css';
import App from './App.vue';
import maplibregl from 'maplibre-gl';
import * as pmtiles from "pmtiles";

const protocol = new pmtiles.Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);

maplibregl.setRTLTextPlugin(
  'https://unpkg.com/@mapbox/mapbox-gl-rtl-text@0.2.3/mapbox-gl-rtl-text.js',
  true // lazy: only fetched once RTL text is actually encountered
);

const app = createApp(App)

app.use(createPinia())

app.mount('#app')
