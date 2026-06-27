import { createApp } from 'vue';
import {createPinia} from 'pinia';
import './style.css';
import App from './App.vue';
import maplibregl from 'maplibre-gl';
import * as pmtiles from "pmtiles";

const protocol = new pmtiles.Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);

const app = createApp(App)

app.use(createPinia())

app.mount('#app')
