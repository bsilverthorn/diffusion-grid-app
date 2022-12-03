<script>
import { useGridStore } from './stores/grid';
import GridImage from './GridImage.vue';

export default {
    name: 'App',
    components: {
        GridImage,
    },
    setup: () => ({
        gridStore: useGridStore(),
    }),
    data() {
        return {
            hoveredBranch: undefined,
            hoveredTimestep: undefined,
        };
    },
    methods: {
        branchSelect(timestep, column) {
            this.gridStore.changeTrunk(timestep, column);
        },
        branchHoverStart(timestep, column) {
            this.hoveredBranch = this.gridStore.branches[timestep][column];
            this.hoveredTimestep = timestep;
        },
        branchHoverStop() {
            this.hoveredBranch = undefined;
            this.hoveredTimestep = undefined;
        },
    },
};
</script>

<template>
<div class="grid place-items-center h-screen">
<div v-if="gridStore.prompt !== undefined" class="grid grid-rows-[repeat(4,_20vmin)] grid-cols-[repeat(5,_20vmin)] drop-shadow-md">

<!-- latents sidebar -->
<div class="row-start-1 row-span-3 col-start-1">
    <div class="grid grid-rows-15 grid-cols-5 h-full">
        <template v-for="(latentsInfo, i) in gridStore.trunk.trajectory?.values()" :key="i">
            <img
                :src="`data:image/jpeg;base64,${hoveredBranch?.trajectory.get(latentsInfo.timestep)?.image ?? latentsInfo.image}`"
                :title="`t = ${latentsInfo.timestep}`"
                :class="`row-start-${2 + i * 5}`"
                class="row-span-3 col-start-2 col-span-3">
            <div v-if="i == 0" class="row-start-1 col-start-3 grid place-items-center">
                <!-- tall vertical ellipsis -->
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 42" stroke-width="1.5" stroke="currentColor" class="w-[2vmin] h-[4vmin] relative top-[-2vmin]">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M12 6.75a.75.75 0 110-1.5.75.75 0 010 1.5z
                           M12 18.75a.75.75 0 110-1.5.75.75 0 010 1.5z
                           M12 30.75a.75.75 0 110-1.5.75.75 0 010 1.5z" />
                </svg>
             </div>
            <div v-if="i > 0" :class="`row-start-${i * 5}`" class="row-span-2 col-start-3 grid place-items-center">
                <!-- tall vertical ellipsis -->
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 42" stroke-width="1.5" stroke="currentColor" class="w-[2vmin] h-[4vmin]">
                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M12 6.75a.75.75 0 110-1.5.75.75 0 010 1.5z
                           M12 18.75a.75.75 0 110-1.5.75.75 0 010 1.5z
                           M12 30.75a.75.75 0 110-1.5.75.75 0 010 1.5z" />
                </svg>
            </div>
            <div :class="`row-start-${3 + i * 5}`" class="col-start-5 text-2xl grid place-items-center">
                <!-- right arrow -->
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-[2vmin] h-[2vmin]">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                </svg>
            </div>
            <div v-if="i == gridStore.trunk.trajectory.size - 1" :class="`row-start-${5 + i * 5}`" class="row-span-2 col-start-3 text-2xl grid place-items-center">
                <!-- down arrow -->
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-[2vmin] h-[2vmin]">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 13.5L12 21m0 0l-7.5-7.5M12 21V3" />
                </svg>
            </div>
        </template>
    </div>
</div>

<!-- grid images -->
<template v-for="timestep in gridStore.timesteps" :key="timestep">
    <grid-image
        v-for="(branch, j) in gridStore.branches[timestep]"
        :key="j"
        :image="branch.image"
        :loading="branch.abort !== undefined"
        :muted="hoveredTimestep !== undefined && hoveredTimestep > timestep"
        class="cursor-pointer"
        @select="branchSelect(timestep, j)"
        @hover-start="branchHoverStart(timestep, j)"
        @hover-stop="branchHoverStop">
    </grid-image>
</template>

<!-- trunk image -->
<div class="relative row-start-4">
    <grid-image
        :loading="gridStore.trunk.abort !== undefined"
        :image="hoveredBranch?.image ?? gridStore.trunk.image">
    </grid-image>
</div>

<!-- prompt and controls -->
<div class="row-start-4 col-start-2 col-end-6 m-[1vmin] relative">
    <div class="grid place-items-center h-full text-slate-700 leading-relaxed text-center text-[3vmin] p-[2vmin] font-serif">
        “{{ gridStore.prompt.text }}”
    </div>
    <div class="absolute bottom-0 right-0">
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
</div>

</div>
</div>
</template>
