<script>
import { useGridStore } from './stores/grid';
import GridImage from './GridImage.vue';
import Controls from './Controls.vue';
import Trajectory from './Trajectory.vue';

export default {
    name: 'App',
    components: {
        GridImage,
        Controls,
        Trajectory,
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
    <trajectory :hovered="hoveredBranch">
    </trajectory>
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
    <controls class="absolute bottom-0 right-0">
    </controls>
</div>

</div>
</div>
</template>
