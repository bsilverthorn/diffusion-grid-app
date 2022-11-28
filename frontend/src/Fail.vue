<script>
export default {
    data() {
        return {
            shown: false,
        };
    },
    methods: {
        show() {
            this.shown = true;
        },
    },
    expose: [
        'show',
    ],
};
</script>

<template>
<div v-if="shown" class="absolute bottom-0 right-0 bg-yellow-200 m-[2vmin] p-[1vmin]">
    <h1 class="text-xl">Something went wrong. 😞</h1>
</div>
</template>