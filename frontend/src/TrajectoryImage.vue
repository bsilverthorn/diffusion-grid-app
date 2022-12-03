<script>
export default {
    props: {
        image: String,
        muted: Boolean,
        loading: Boolean,
    },
    data() {
        return {
            hovered: false,
        };
    },
    computed: {
        loaded() {
            // image may be (loaded, not loading) or (not loaded, [not] loading)
            return this.image !== undefined;
        },
        src() {
            return this.loaded ? `data:image/jpeg;base64,${this.image}` : '';
        },
    },
    methods: {
        click() {
            if(this.loaded) {
                this.$emit('select');
            }
        },
        mouseEnter() {
            if(this.loaded) {
                this.hovered = true;

                this.$emit('hoverStart');
            }
        },
        mouseLeave() {
            if(this.loaded || this.hovered) {
                this.hovered = false;

                this.$emit('hoverStop');
            }
        },
    },
    emits: ['select', 'hoverStart', 'hoverStop'],
};
</script>

<template>
<div
    class="grid place-items-center h-full relative p-[1vmin]"
    @click="click"
    @mouseenter="mouseEnter"
    @mouseleave="mouseLeave">
    <img
        :src="src"
        :class="{ 'grayscale': muted, 'invisible': !loaded }"
        height="512"
        width="512">
    <svg v-if="loading" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="animate-spin -ml-1 mr-3 h-[3vmin] w-[3vmin] absolute">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
</div>
</template>
