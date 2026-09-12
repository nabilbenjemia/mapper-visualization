<template>
  <div class="category-modes">
    <!-- Categories -->
    <div class="category-section">
      <div class="section-title">
        Categories
      </div>

      <div class="category-list">
        <button
          v-for="category in dataset.categories"
          :key="category.category"
          class="category-button"
          :class="{
            active:
              selectedCategory === category.category
          }"
          @click="selectedCategory = category.category"
        >
          {{ formatName(category.category) }}
        </button>
      </div>
    </div>

    <!-- Modes -->
    <div
      v-if="selectedCategoryData"
      class="mode-section"
    >
      <div class="section-title">
        {{ formatName(selectedCategoryData.category) }}
      </div>

      <div class="mode-list">
        <div
          v-for="mode in selectedCategoryData.modes"
          :key="mode.mode"
          class="mode-row"
        >
          <div class="mode-row-top">
            <span class="mode-name">
              {{ formatName(mode.mode) }}
            </span>

            <div class="mode-actions">
              <span class="status"
                :class="{
                  available:
                    mode.available &&
                    !getBuildStatus(selectedCategory, mode.mode),

                  processing:
                    getBuildStatus(selectedCategory, mode.mode) ===
                    'PROCESSING',

                  error:
                    getBuildStatus(selectedCategory, mode.mode) ===
                    'ERROR',

                  unavailable:
                    !mode.available &&
                    !getBuildStatus(selectedCategory, mode.mode)
                }"
              >
                <span class="status-dot"></span>

                {{
                  getBuildStatus(selectedCategory, mode.mode) ===
                  "PROCESSING"
                    ? "Processing"
                    : getBuildStatus(selectedCategory, mode.mode) ===
                      "ERROR"
                      ? "Error"
                      : mode.available
                        ? "Available"
                        : "Not available"
                }}
              </span>

              <button
                v-if="
                  !mode.available &&
                  getBuildStatus(selectedCategory, mode.mode) !==
                    'PROCESSING'
                "
                class="mode-build-button"
                :disabled="isDatasetBuilding"
                @click="buildMode(mode.mode)"
              >
                Build
              </button>
            </div>
          </div>

          <p
            v-if="getJobError(selectedCategory, mode.mode)"
            class="mode-error"
          >
            {{ getJobError(selectedCategory, mode.mode) }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue"

const props = defineProps({
  dataset: {
    type: Object,
    required: true,
  },
  buildStatuses: {
    type: Object,
    default: () => ({}),
  },
  jobErrors: {
    type: Object,
    default: () => ({}),
  },
})

function getBuildStatus(category, mode) {
  return props.buildStatuses[
    `${props.dataset.dataset}:${category}:${mode}`
  ]
}

function getJobError(category, mode) {
  if (getBuildStatus(category, mode) !== "ERROR") {
    return null
  }

  return props.jobErrors[
    `${props.dataset.dataset}:${category}:${mode}`
  ]
}

const emit = defineEmits(["build-mode"])

const selectedCategory = ref(
  props.dataset.categories?.[0]?.category ?? null
)

const selectedCategoryData = computed(() => {
  return props.dataset.categories?.find(
    category =>
      category.category === selectedCategory.value
  )
})

function buildMode(mode) {
  emit("build-mode", {
    dataset: props.dataset.dataset,
    category: selectedCategory.value,
    mode,
  })
}

function formatName(value) {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, char => char.toUpperCase())
}

const isDatasetBuilding = computed(() => {
  return (
    props.buildStatuses[`dataset:${props.dataset.dataset}`] ===
    "PROCESSING"
  )
})

</script>

<style scoped>
.category-modes {
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 0.0625rem solid #eee;
}

.section-title {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.625rem;
}

/* Categories */

.category-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;

  max-height: 9rem;
  overflow-y: auto;
  padding: 0.125rem;
}

.category-button {
  padding: 0.4rem 0.65rem;

  border: 0.0625rem solid #ccc;
  border-radius: 0.375rem;

  background: transparent;
  color: var(--text);

  font-size: 0.8rem;
  cursor: pointer;
}

.category-button:hover {
  background: #f3f4f6;
}

.category-button.active {
  background: #2563eb;
  border-color: #2563eb;
  color: white;
}

/* Modes */

.mode-section {
  margin-top: 1.25rem;
}

.mode-list {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.mode-row {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;

  min-height: 2.5rem;
  padding: 0.5rem 0.75rem;

  border: 0.0625rem solid #eee;
  border-radius: 0.375rem;

  background: var(--bg);
}

.mode-row-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.mode-error {
  margin: 0;
  font-size: 0.75rem;
  color: #dc2626;
}

.mode-name {
  font-size: 0.85rem;
}

.mode-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.status {
  display: flex;
  align-items: center;
  gap: 0.35rem;

  font-size: 0.75rem;
}

.status-dot {
  width: 0.4rem;
  height: 0.4rem;
  border-radius: 50%;
}

.status.available {
  color: #16a34a;
}

.status.available .status-dot {
  background: #16a34a;
}

.status.unavailable {
  color: #777;
}

.status.unavailable .status-dot {
  background: #999;
}

.mode-build-button {
  padding: 0.3rem 0.6rem;

  border: 0.0625rem solid #2563eb;
  border-radius: 0.35rem;

  background: transparent;
  color: #2563eb;

  font-size: 0.75rem;
  cursor: pointer;
}

.mode-build-button:hover {
  background: #eff6ff;
}

.status.processing {
  color: #2563eb;
}

.status.error {
  color: #dc2626;
}

.status.error .status-dot {
  background: #dc2626;
}

.status.processing .status-dot {
  background: #2563eb;
  animation: pulse 1.2s infinite;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.35;
  }
}
</style>