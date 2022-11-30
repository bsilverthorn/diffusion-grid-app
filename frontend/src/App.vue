<script>
import TrajectoryImage from './TrajectoryImage.vue';

export default {
    components: {
        TrajectoryImage,
    },
    data() {
        return {
            prompts: [],
            promptIndex: 0,
            branchPoints: [],
            seed: 42,
            seedIncrement: 16,
            hoveredBranch: undefined,
            hoveredTimestep: undefined,
            srcForce: undefined,
            srcHover: undefined,
        };
    },
    computed: {
        prompt() {
            const d = this.prompts.length;

            return this.prompts[((this.promptIndex % d) + d) % d];
        },
        latentImages() {
            return this.branchPoints.map(point => {
                if(this.hoveredBranch !== undefined && this.hoveredBranch[point.timestep] !== undefined) {
                    return {
                        ...point,
                        image: this.hoveredBranch[point.timestep].image,
                    }
                }
                else {
                    return point;
                }
            });
        },
    },
    methods: {
        mainBranchLoaded(branch, signatures) {
            this.branchPoints = branch.slice().sort((a, b) => b.timestep - a.timestep);
        },
        changePrompt(increment) {
            this.branchPoints = [];
            this.srcForce = undefined;
            this.promptIndex += increment;
        },
        sideBranchClick(branch, src) {
            const branchByTimestep = Object.fromEntries(
                branch.map(point => [point.timestep, point])
            );

            this.srcForce = src;
            this.branchPoints = this.branchPoints.map(point => {
                if(branch !== undefined && branchByTimestep[point.timestep] !== undefined) {
                    return {
                        ...branchByTimestep[point.timestep],
                        timestep: point.timestep,
                    };
                }
                else {
                    return point;
                }
            });
        },
        sideBranchHoverStart(branch, src, timestep) {
            this.srcHover = src;
            this.hoveredBranch = branch;
            this.hoveredTimestep = timestep;
        },
        sideBranchHoverStop() {
            this.srcHover = undefined;
            this.hoveredBranch = undefined;
            this.hoveredTimestep = undefined;
        },
        incrementSeed() {
            this.branchPoints = [];
            this.srcForce = undefined;
            this.seed += this.seedIncrement;
        },
    },
    mounted() {
        return this.api.get('/prompts')
            .then((data) => { this.prompts = data; });
    },
};
</script>

<template>
<div class="grid place-items-center h-screen">
<div v-if="prompt !== undefined" class="grid grid-rows-[repeat(4,_20vmin)] grid-cols-[repeat(5,_20vmin)] drop-shadow-md">

<div class="row-start-1 row-span-3 col-start-1">
    <div class="grid grid-rows-15 grid-cols-5 h-full">
        <template v-for="(point, i) in latentImages" :key="point.timestep">
            <img
                :src="`data:image/jpeg;base64,${point.image}`"
                :title="`t = ${point.timestep}`"
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
            <div v-if="i == latentImages.length - 1" :class="`row-start-${5 + i * 5}`" class="row-span-2 col-start-3 text-2xl grid place-items-center">
                <!-- down arrow -->
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-[2vmin] h-[2vmin]">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 13.5L12 21m0 0l-7.5-7.5M12 21V3" />
                </svg>
            </div>
        </template>
    </div>
</div>

<template v-for="(point, i) in branchPoints" :key="point.timestep">
    <trajectory-image
        v-for="j in 4"
        :key="j"
        :prompt="prompt.text"
        :timestep="point.timestep"
        :latents="point.tensor"
        :signature="point.signature"
        :seed="seed + i * branchPoints.length + j + 1"
        :muted="hoveredTimestep !== undefined && hoveredTimestep > point.timestep"
        class="cursor-pointer"
        @branch-click="sideBranchClick"
        @branch-hover-start="(branch, src) => sideBranchHoverStart(branch, src, point.timestep)"
        @branch-hover-stop="sideBranchHoverStop">
    </trajectory-image>
</template>

<div class="relative row-start-4">
    <trajectory-image
        :prompt="prompt.text"
        :signature="prompt.signature"
        :src-force="srcForce"
        :seed="seed"
        @loaded="mainBranchLoaded">
    </trajectory-image>
    <div v-if="srcHover" class="absolute top-0 left-0 p-[1vmin]">
        <img :src="srcHover" height="512" width="512">
    </div>
</div>

<div class="row-start-4 col-start-2 col-end-6 m-[1vmin] relative">
    <div class="grid place-items-center h-full text-purple-800 leading-relaxed text-center text-[3vmin] p-[2vmin] font-serif">
        “{{ prompt.text }}”
    </div>
    <div class="absolute bottom-0 right-0">
        <button type="button" @click="changePrompt(-1)">
            <!-- left chevron -->
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-[2vmin] h-[2vmin] hover:stroke-purple-600">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
            </svg>
        </button>
        <button type="button" @click="incrementSeed">
            <!-- refresh symbol -->
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-[2vmin] h-[2vmin] hover:stroke-purple-600">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99" />
            </svg>
        </button>
        <button type="button" @click="changePrompt(1)">
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
