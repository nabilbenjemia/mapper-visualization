<script setup>
import tumLogo from '../assets/tum_logo.png';
import mapperLogo from '../assets/mapper_logo_long.svg';
import { useThemeStore } from '../stores/theme';

const theme = useThemeStore();

defineEmits(['go-home'])
</script>

<template>
  <header class="header">
    <div class="logo">
      <img
        :src="mapperLogo"
        alt="Logo"
        @click="$emit('go-home')"
      />
    </div>

    <button class="theme-btn" @click="theme.toggle()">
      <span class="material-symbols-outlined">
        {{ theme.dark ? 'light_mode' : 'dark_mode' }}
      </span>
    </button>
  </header>
</template>

<style scoped>
.header {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 64px;

  display: flex;
  justify-content: center;
  align-items: center;

  background: var(--bg);
  color: var(--text);

  z-index: 1000;
  box-shadow: 0 1px 4px rgba(0,0,0,0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 6px;
}

.logo img {
  width: 120px;
  cursor: pointer;
}

.theme-btn {
  position: absolute;
  right: 24px;

  padding: 8px;
  border-radius: 50%;
  background: transparent;
  border: none;

  cursor: pointer;
  transition: background 0.2s;
}

.theme-btn:hover {
  background: rgba(0,0,0,0.05);
}
</style>

