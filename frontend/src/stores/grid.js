import { defineStore } from 'pinia';
import objectHash from 'object-hash';

const GRID_CONFIG = {
    timesteps: [921, 821, 701],
    columns: 4,
};

export const useGridStore = defineStore('grid', {
    state() {
        const branches = Object.fromEntries(
            GRID_CONFIG.timesteps.map(
                t => [t, Array(GRID_CONFIG.columns).fill().map(() => ({}))]
            )
        );

        return {
            prompts: [],
            promptIndex: 0,
            timesteps: GRID_CONFIG.timesteps,
            trunk: {},
            branches: branches,
        };
    },
    getters: {
        prompt() {
            const d = this.prompts.length;

            return this.prompts[((this.promptIndex % d) + d) % d];
        },
    },
    actions: {
        load() {
            this.api.fetchPrompts().then(prompts => {
                this.prompts = prompts.map(prompt => ({
                    salts: { all: 1, grid: {} },
                    ...prompt,
                }));
            })
            .then(() => {
                this.loadTrunk();
            });
        },
        loadTrunk() {
            this.clearTrunk();
            this.clearBranchesAt(this.timesteps);

            const { abort, request } = this.api.fetchBranch(
                this.prompt,
                null,
                null,
                this.getSeed(),
                this.timesteps,
            );

            this.trunk = { abort };

            return request.then(trunk => {
                this.trunk = trunk;

                this.loadBranchesAt(this.timesteps);
            });
        },
        loadBranch(timestep, column) {
            this.clearBranch(timestep, column);

            const { abort, request } = this.api.fetchBranch(
                this.prompt,
                this.trunk.trajectory.get(timestep),
                timestep,
                this.getSeed(timestep, column),
                this.timesteps,
            );

            this.branches[timestep][column] = { abort };

            return request.then(branch => {
                this.branches[timestep][column] = branch;
            });
        },
        loadBranchesAt(timesteps) {
            for (const t of timesteps) {
                for (let i = 0; i < GRID_CONFIG.columns; ++i) {
                    this.loadBranch(t, i);
                }
            }
        },
        clearTrunk() {
            this.trunk.abort?.abort();
            this.trunk = {};
        },
        clearBranch(timestep, column) {
            this.branches[timestep][column].abort?.abort();
            this.branches[timestep][column] = {};
        },
        clearBranchesAt(timesteps) {
            for (const t of timesteps) {
                for (let i = 0; i < GRID_CONFIG.columns; ++i) {
                    this.clearBranch(t, i);
                }
            }
        },
        changePrompt(increment) {
            this.promptIndex += increment;

            this.loadTrunk();
        },
        changeTrunk(timestep, column) {
            // overwrite trunk with branch
            const branch = this.branches[timestep][column];

            this.trunk.image = branch.image;
            this.trunk.trajectory = new Map(
                function* () {
                    for (const [t, v] of this.trunk.trajectory) {
                        yield [t, branch.trajectory.get(t) ?? v];
                    }
                }.call(this)
            );

            // regenerate affected branches
            this.reseedBranch(timestep, column);
            this.reseedBranchesAt(branch.trajectory.keys(), null);
        },
        reseedAll() {
            this.prompt.salts.all += 1;
            this.prompt.salts.grid = {};

            this.loadTrunk();
        },
        reseedBranch(timestep, column, increment = 1) {
            const saltKey = this.getSaltKey(timestep, column);

            if(increment === null) {
                delete this.prompt.salts.grid[saltKey];
            }
            else {
                this.prompt.salts.grid[saltKey] ??= 0;
                this.prompt.salts.grid[saltKey] += increment;
            }

            this.loadBranch(timestep, column);
        },
        reseedBranchesAt(timesteps, increment = 1) {
            for (const t of timesteps) {
                for (let i = 0; i < GRID_CONFIG.columns; ++i) {
                    this.reseedBranch(t, i, increment);
                }
            }
        },
        getSaltKey(timestep, column) {
            return `b${timestep}x${column}`;
        },
        getSeed(timestep, column) {
            const hashed = objectHash([
                timestep,
                column,
                this.prompt.salts.all,
                this.prompt.salts.grid[this.getSaltKey(timestep, column)],
            ]);

            return parseInt(hashed.slice(-8), 16);
        },
    },
});
