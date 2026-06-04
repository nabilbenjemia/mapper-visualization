<script setup>
import tumLogo from '../assets/tum_logo.png';
import mapperLogo from '../assets/mapper_logo_long.svg';
</script>

<template>
  <header class="absolute top-0 left-0 w-full h-16 bg-white flex justify-center items-center z-[1000] shadow-sm">
    <div class="flex items-center gap-1.5">
      <img :src="mapperLogo" alt="Logo" class="w-30 rounded" />
      <span class="font-semibold tracking-widest"></span>
    </div>
  </header>
</template>