<template>
  <div class="dataset-card">
    <h2 class="dataset-name">
      {{ dataset.dataset }}
    </h2>

    <div v-if="showDetails" class="details">
      <p>
        <strong>Status:</strong>
        {{ dataset.pmtiles.status }}
      </p>

      <p>
        <strong>Tiles:</strong>
        {{ dataset.pmtiles.available }} / {{ dataset.pmtiles.expected }}
      </p>

      <p>
        <strong>Region:</strong>
        {{ dataset.region ?? "-" }}
      </p>

      <p>
        <strong>Source:</strong>
        {{ dataset.source_available ? "Available" : "Missing" }}
      </p>

      <CategoryModes
        :dataset="dataset"
        :build-statuses="buildStatuses"
        @build-mode="buildMode"
      />
    </div>



    <p v-if="error" class="build-error">
      {{ error }}
    </p>

    <div class="actions">
      <button
        class="details-button"
        @click="showDetails = !showDetails"
      >
        {{ showDetails ? "Hide Details" : "Details" }}
      </button>

      <button
        class="build-button"
        :disabled="isBuilding"
        @click="$emit('build', dataset)"
      >
        {{ isBuilding ? "Processing..." : "Build Tiles" }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"
import CategoryModes from "./CategoryModes.vue"

const props = defineProps({
  dataset: {
    type: Object,
    required: true,
  },
  buildStatuses: {
    type: Object,
    default: () => ({}),
  },
  error: {
    type: String,
    default: null,
  },
})

const isBuilding = computed(() => {
  return (
    props.buildStatuses[`dataset:${props.dataset.dataset}`] ===
    "PROCESSING"
  )
})

const emit = defineEmits([
  "build",
  "build-mode",
])

const showDetails = ref(false)

function buildMode(data) {
  emit("build-mode", data)
}
</script>

<style scoped>
.dataset-card {
  width: 100%;
  border: 0.0625rem solid #ddd;
  border-radius: 0.625rem;
  background: var(--bg);
  color: var(--text);
  padding: 1.25rem;
  box-shadow: 0 0.125rem 0.5rem rgba(0, 0, 0, 0.08);
}

.dataset-name {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 1rem;
  word-break: break-all;
}

.details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #555;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 0.0625rem solid #eee;
}

.details p {
  margin: 0;
}

.build-error {
  margin-top: 0.75rem;
  font-size: 0.8rem;
  color: #dc2626;
  text-align: right;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.build-button {
  background: #2563eb;
  border: none;
  color: white;
}

.build-button:hover {
  background: #1d4ed8;
}

.details-button {
  background: white;
  border: 0.0625rem solid #ccc;
  color: #333;
}

.details-button:hover {
  background: #f3f4f6;
}

.build-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>