<template>
    <div class="dataset-metadata">
        <h2>Dataset Information</h2>

        <div v-if="metadata">
            <div v-if="metadata.kernel">
                <div class="metadata-row">
                    <span class="label">Kernel</span>
                    <span class="value">{{ metadata.kernel.type }}</span>
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
    padding: 12px 16px;

    background: var(--bg);
    color: var(--text);

    border: 1px solid #e5e7eb;
    border-radius: 10px;

    box-shadow: 0 2px 8px rgb(0 0 0 / 12%);
}

.dataset-metadata h2 {
    margin: 0 0 12px;
    font-size: 16px;
    font-weight: 600;
    text-align: center;
}

.dataset-metadata p {
    margin: 4px 0;
    font-size: 14px;
    line-height: 1.4;
}

.dataset-metadata strong {
    color: var(--text);
}

.section {
    margin-top: 10px;
}

.kernel-list {
    margin-left: 8px;
}

.metadata-row {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    margin: 6px 0;
}

.label {
    font-weight: 600;
}

.value {
    text-align: right;
}
</style>