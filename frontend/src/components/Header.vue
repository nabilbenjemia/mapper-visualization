<script setup>
import tumLogo from '../assets/tum_logo.png';
</script>

<template>
  <header class="absolute top-0 left-0 w-full h-16 bg-white flex justify-center items-center z-[1000] shadow-sm">
    <div class="flex items-center gap-2.5">
      <img :src="tumLogo" alt="Logo" class="w-16 rounded" />
      <span class="font-semibold tracking-widest">MAPPER</span>
    </div>
  </header>
</template>