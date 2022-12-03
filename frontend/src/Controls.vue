<script>
import { useGridStore } from './stores/grid';

export default {
    setup: () => ({
        gridStore: useGridStore(),
    }),
};
</script>

<template>
<div>
    <button type="button" @click="gridStore.changePrompt(-1)">
        <!-- left chevron -->
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-[2vmin] h-[2vmin] hover:stroke-purple-600">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
        </svg>
    </button>
    <button type="button" class="ml-[0.20vmin]" @click="gridStore.reseedAll()">
        <!-- refresh symbol -->
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-[2vmin] h-[2vmin] hover:stroke-purple-600">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
        </svg>
    </button>
    <a href="https://github.com/bsilverthorn/diffusion-grid-app#diffusion-grid" target="_blank" class="ml-[0.25vmin] inline-block">
        <!-- info symbol -->
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-[2vmin] h-[2vmin] hover:stroke-purple-600">
            <path stroke-linecap="round" stroke-linejoin="round" d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z" />
        </svg>
    </a>
    <button type="button" @click="gridStore.changePrompt(1)">
        <!-- right chevron -->
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-[2vmin] h-[2vmin] hover:stroke-purple-600">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
        </svg>
    </button>
</div>
</template>
