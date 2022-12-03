<script>
import { useGridStore } from './stores/grid';

export default {
    setup: () => ({
        gridStore: useGridStore(),
    }),
    props: {
        hovered: Object,
    },
};
</script>

<template>
<div class="grid grid-rows-15 grid-cols-5 h-full">

<template v-for="(latentsInfo, i) in gridStore.trunk.trajectory?.values()" :key="i">
    <img
        :src="`data:image/jpeg;base64,${hovered?.trajectory.get(latentsInfo.timestep)?.image ?? latentsInfo.image}`"
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
</template>
