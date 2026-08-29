<template>
  <div class="dataset-view">
    <h1 class="title">Datasets</h1>

    <div class="dataset-list">
      <DatasetCard
        v-for="dataset in datasets"
        :key="dataset.dataset"
        :dataset="dataset"
        :build-statuses="buildStatuses"
        @build="buildDataset"
        @build-mode="buildTiles"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue"
import DatasetCard from "./DatasetCard.vue"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const datasets = ref([])

const buildStatuses = ref({})

function getBuildKey(dataset, category, mode) {
  return `${dataset}:${category}:${mode}`
}

function getDatasetBuildKey(dataset) {
  return `dataset:${dataset}`
}

async function loadDatasets() {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/datasets`)

    if (!response.ok) {
      throw new Error(`Failed loading datasets (${response.status})`)
    }

    datasets.value = await response.json()
    console.log("Loaded datasets:", datasets.value)
  } catch (error) {
    console.error("Could not load datasets:", error)
  }
}

async function buildDataset(dataset) {
  const key = getDatasetBuildKey(dataset.dataset)

  buildStatuses.value[key] = "PROCESSING"

  try {
    const response = await fetch(
      `${API_BASE_URL}/admin/datasets/${dataset.dataset}/build`,
      {
        method: "POST",
      }
    )

    if (!response.ok) {
      throw new Error(
        `Failed building dataset (${response.status})`
      )
    }

    const job = await response.json()

    console.log(
      `Started building dataset ${dataset.dataset}`,
      job.job_id
    )

    pollJob(job.job_id, key)

  } catch (error) {
    console.error(
      `Could not build dataset ${dataset.dataset}:`,
      error
    )

    buildStatuses.value[key] = "ERROR"
  }
}

async function buildTiles({ dataset, category, mode }) {
  const key = getBuildKey(dataset, category, mode)

  buildStatuses.value[key] = "PROCESSING"
  
  console.log(
    "BUILD STATUS SET:",
    key,
    buildStatuses.value
  )


  try {
    const response = await fetch(
      `${API_BASE_URL}/admin/datasets/${dataset}/build/${category}/${mode}`,
      {
        method: "POST",
      }
    )

    if (!response.ok) {
      throw new Error(
        `Failed building tiles (${response.status})`
      )
    }

    const job = await response.json()

    console.log(
      `Started building ${dataset}/${category}/${mode}`,
      job.job_id
    )

    pollJob(job.job_id, key)

  } catch (error) {
    console.error(
      `Could not build tiles for ${dataset}/${category}/${mode}:`,
      error
    )

    buildStatuses.value[key] = "ERROR"
  }
}

async function pollJob(jobId, key) {
  try {
    const response = await fetch(
      `${API_BASE_URL}/admin/jobs/${jobId}`
    )

    if (!response.ok) {
      throw new Error(
        `Failed to get job status (${response.status})`
      )
    }

    const job = await response.json()

    buildStatuses.value[key] = job.status

    if (job.status === "PROCESSING") {
      setTimeout(() => {
        pollJob(jobId, key)
      }, 1000)

      return
    }

    if (job.status === "SUCCESS") {
      console.log(`Build completed: ${jobId}`)

      delete buildStatuses.value[key]

      await loadDatasets()

      return
    }

    if (job.status === "ERROR") {
      console.error(
        `Build failed: ${job.error}`
      )

      return
    }

  } catch (error) {
    console.error(
      `Could not retrieve job status for ${jobId}:`,
      error
    )

    setTimeout(() => {
      pollJob(jobId, key)
    }, 1000)
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