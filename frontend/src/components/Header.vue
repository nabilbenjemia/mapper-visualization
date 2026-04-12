<script setup>
import tumLogo from '../assets/tum_logo.png';
</script>

<template>
  <header class="navbar">
    <div class="logo-area">
      <img :src="tumLogo" alt="Logo" class="logo-placeholder" />
      <span class="logo-text">MAPPER</span>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  position: absolute; /* Floats over the map */
  top: 0;
  left: 0;
  width: 100%;
  height: 60px;
  background: white;
  display: flex;
  justify-content: center; /* Logo in the middle */
  align-items: center;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-placeholder {
  width: 60px;
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 4px;
  font-weight: bold;
}

.logo-text {
  font-weight: 600;
  letter-spacing: 1px;
}
</style>