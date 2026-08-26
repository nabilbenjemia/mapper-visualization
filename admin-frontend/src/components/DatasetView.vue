<template>
  <div class="dataset-view">
    <h1 class="title">Datasets</h1>

    <div class="dataset-list">
      <DatasetCard
        v-for="dataset in datasets"
        :key="dataset.dataset"
        :dataset="dataset"
        @build="buildDataset"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import DatasetCard from "./DatasetCard.vue"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const datasets = ref([])

async function loadDatasets() {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/datasets`)

    if (!response.ok) {
      throw new Error(`Failed loading datasets (${response.status})`)
    }

    datasets.value = await response.json()
  } catch (error) {
    console.error("Could not load datasets:", error)
  }
}

async function buildDataset(dataset) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/admin/datasets/${dataset.dataset}/build`,
      {
        method: "POST",
      }
    )

    if (!response.ok) {
      throw new Error(`Failed building dataset (${response.status})`)
    }

    await loadDatasets()
  } catch (error) {
    console.error("Could not build dataset:", error)
  }
}

onMounted(loadDatasets)
</script>

<style scoped>
.dataset-view {
  width: 100%;
  max-width: 75rem;
  margin: 0 auto;
  padding: 2.5rem;
  background: var(--bg);
  color: var(--text);
}

.title {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.dataset-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>