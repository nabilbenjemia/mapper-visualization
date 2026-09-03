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
import { onMounted, onUnmounted, ref } from "vue"
import DatasetCard from "./DatasetCard.vue"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const datasets = ref([])
const buildStatuses = ref({})

let jobsPollingInterval = null

function getBuildKey(dataset, category, mode) {
  return `${dataset}:${category}:${mode}`
}

function getDatasetBuildKey(dataset) {
  return `dataset:${dataset}`
}

async function loadDatasets() {
  try {
    const response = await fetch(
      `${API_BASE_URL}/admin/datasets`
    )

    if (!response.ok) {
      throw new Error(
        `Failed loading datasets (${response.status})`
      )
    }

    datasets.value = await response.json()

    console.log("Loaded datasets:", datasets.value)

  } catch (error) {
    console.error(
      "Could not load datasets:",
      error
    )
  }
}

async function loadJobs() {
  try {
    const response = await fetch(
      `${API_BASE_URL}/admin/jobs`
    )

    if (!response.ok) {
      throw new Error(
        `Failed loading jobs (${response.status})`
      )
    }

    const jobs = await response.json()

    const statuses = {}

    for (const job of jobs) {

      // Child job: category × mode
      if (job.category && job.mode) {

        const key = getBuildKey(
          job.dataset,
          job.category,
          job.mode
        )

        statuses[key] = job.status

      }

      // Parent job: Build All
      else {

        const key = getDatasetBuildKey(
          job.dataset
        )

        statuses[key] = job.status
      }
    }

    buildStatuses.value = statuses

  } catch (error) {
    console.error(
      "Could not load jobs:",
      error
    )
  }
}


function startJobsPolling() {

  loadJobs()

  // Load jobs every 3 seconds
  jobsPollingInterval = setInterval(() => {
    loadJobs()
  }, 3000)
}


function stopJobsPolling() {

  if (jobsPollingInterval) {
    clearInterval(jobsPollingInterval)
    jobsPollingInterval = null
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
      throw new Error(
        `Failed building dataset (${response.status})`
      )
    }

    const job = await response.json()

    console.log(
      `Started building dataset ${dataset.dataset}`,
      job.job_id
    )

    // Immediately refresh job state
    await loadJobs()

  } catch (error) {

    console.error(
      `Could not build dataset ${dataset.dataset}:`,
      error
    )
  }
}

async function buildTiles({ dataset, category, mode }) {

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

    await loadJobs()

  } catch (error) {

    console.error(
      `Could not build tiles for ${dataset}/${category}/${mode}:`,
      error
    )
  }
}

onMounted(async () => {

  await loadDatasets()

  await loadJobs()

  startJobsPolling()
})

onUnmounted(() => {
  stopJobsPolling()
})
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