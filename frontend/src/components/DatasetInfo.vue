<template>
    <div class="dataset-metadata">
        <h2>Dataset Information</h2>

        <div v-if="metadata">
            <div v-if="metadata.kernel">
                <div class="metadata-row">
                    <span class="label">Kernel</span>
                    <span class="value">{{ metadata.kernel.type.charAt(0).toUpperCase() + metadata.kernel.type.slice(1) }}</span>
                </div>

                <div v-if="metadata.kernel.sigma" class="metadata-row">
                    <span class="label">Sigma</span>
                    <span class="value">{{ metadata.kernel.sigma }}</span>
                </div>

                <div v-if="metadata.kernel.bandwidth" class="metadata-row">
                    <span class="label">Bandwidth</span>
                    <span class="value">{{ metadata.kernel.bandwidth }}</span>
                </div>

                <div class="metadata-row">
                    <span class="label">Cutoff</span>
                    <span class="value">{{ metadata.cutoff }}</span>
                </div>

                <div class="metadata-row">
                    <span class="label">Ceiling</span>
                    <span class="value">{{ metadata.ceiling }}</span>
                </div>
            </div>

        </div>

        <p v-else>No metadata available.</p>
    </div>

</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
    metadata: {
        type: Object,
        required: false,
        default: null
    }
})


</script>

<style>
.dataset-metadata {
    padding: 0.75rem 1rem;

    background: var(--bg);
    color: var(--text);

    border: 0.0625rem solid #e5e7eb;
    border-radius: 0.625rem;

    box-shadow: 0 0.125rem 0.5rem rgb(0 0 0 / 12%);
}

.dataset-metadata h2 {
    margin: 0 0 0.75rem;
    font-size: 1rem;
    font-weight: 600;
    text-align: center;
}

.dataset-metadata p {
    margin: 0.25rem 0;
    font-size: 0.875rem;
    line-height: 1.4;
}

.dataset-metadata strong {
    color: var(--text);
}

.section {
    margin-top: 0.625rem;
}

.kernel-list {
    margin-left: 0.5rem;
}

.metadata-row {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    margin: 0.375rem 0;
}

.label {
    font-weight: 600;
}

.value {
    text-align: right;
}
</style>