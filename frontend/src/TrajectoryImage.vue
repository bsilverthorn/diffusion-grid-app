<script>
export default {
    props: {
        srcForce: String,
        prompt: String,
        signature: String,
        latents: String,
        timestep: Number,
        seed: Number,
        muted: Boolean,
    },
    data() {
        return {
            loading: true,
            src: undefined,
            branch: undefined,
            loadAbort: undefined,
        };
    },
    computed: {
        effectiveSrc() {
            return this.srcForce === undefined ? this.src : this.srcForce;
        },
    },
    watch: {
        prompt(newPrompt) {
            this.loadSample();
        },
        latents(newLatents) {
            this.loadSample();
        },
        seed(newSeed) {
            this.loadSample();
        },
    },
    mounted() {
        this.loadSample();
    },
    unmounted() {
        if(this.loadAbort !== undefined) {
            this.loadAbort.abort();
        }
    },
    emits: ['loaded', 'branchClick', 'branchHoverStart', 'branchHoverStop'],
    methods: {
        stringHash(string) {
            return string.split("").reduce((h, c) => h + c.charCodeAt(0), 0);
        },
        loadSample() {
            // clear existing state
            this.loading = true;
            this.src = undefined;
            this.branch = undefined;

            if(this.loadAbort !== undefined) {
                this.loadAbort.abort();

                this.loadAbort = undefined;
            }

            // load new sample from backend
            const requestArgs = new URLSearchParams({
                'signature': this.signature,
            });
            const requestBody = {
                'prompt': this.prompt,
                'seed': this.seed,
                'trajectory_at': [921, 821, 701],
            };

            if(this.latents !== undefined) {
                requestBody['latents'] = this.latents;
                requestBody['timestep'] = this.timestep;
            }

            this.loadAbort = new AbortController();

            fetch(
                `${this.appSettings.apiRoot}/diffusions?` + requestArgs,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestBody),
                    signal: this.loadAbort.signal,
                },
            )
            .then((response) => response.json())
            .then((data) => {
                if(data['call_id'] !== undefined) {
                    return this.checkRequest(data['call_id'], this.loadAbort.signal);
                }
                else {
                    return data;
                }
            })
            .then((data) => {
                this.src = 'data:image/jpeg;base64,' + data['diffusion']['image'];
                this.loading = false;
                this.branch = data['diffusion']['trajectory'].map(
                    (latentsInfo) => {
                        return {
                            ...latentsInfo,
                            signature: data.signatures[latentsInfo.timestep],
                        };
                    }
                );

                this.$emit('loaded', this.branch);
            });
        },
        checkRequest(callId, abortSignal) {
            return fetch(
                `${this.appSettings.apiRoot}/diffusions/${callId}`,
                {
                    signal: abortSignal,
                },
            )
            .then((response) => response.json())
            .then((data) => {
                if(data['call_id'] !== undefined) {
                    return new Promise(resolve => setTimeout(resolve, 1000))
                        .then(() => this.checkRequest(callId, abortSignal));
                }
                else {
                    return data;
                }
            });
        },
    },
};
</script>

<template>
<div
    class="grid place-items-center h-full relative p-[1vmin]"
    @click="$emit('branchClick', branch, src)"
    @mouseenter="$emit('branchHoverStart', branch, src)"
    @mouseleave="$emit('branchHoverStop', branch, src)">
    <img
        :src="effectiveSrc"
        :class="{'grayscale': muted, 'invisible': effectiveSrc === undefined}" 
        height="512"
        width="512">
    <svg v-if="effectiveSrc === undefined" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="animate-spin -ml-1 mr-3 h-[3vmin] w-[3vmin] absolute">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
</div>
</template>
