export class DGAPI {
    constructor(apiRoot, errorListener) {
        this.apiRoot = apiRoot;
        this.errorListener = errorListener;
    }

    call(method, path, data, options = {}) {
        const args = new URLSearchParams(options.args).toString();

        return fetch(
            this.apiRoot + path + (args !== '' ? '?' + args : ''),
            {
                method: method,
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
                signal: options.signal,
            },
        )
        .then(response => {
            if (response.status === 429) {
                const timeout = 1000 + Math.random() * 6400;

                return new Promise(resolve => setTimeout(resolve, timeout))
                    .then(() => this.call(method, path, data, options));
            }
            else {
                return response;
            }
        })
        .then(response => response.json())
        .catch(error => {
            if(error.name !== 'AbortError') {
                this.errorListener(error);
            }

            throw error;
        });
    }

    get(path, options) {
        return this.call('GET', path, undefined, options);
    }

    post(path, data, options) {
        return this.call('POST', path, data, options);
    }

    fetchPrompts() {
        return this.get('/prompts');
    }

    fetchBranch(prompt, latents, timestep, seed, trajectoryAt) {
        const abort = new AbortController();
        const check = (callId) => {
            return this.get(
                `/diffusions/${callId}`,
                {
                    signal: abort.signal,
                },
            )
            .then((data) => {
                if(data['call_id'] !== undefined) {
                    const timeout = new Promise(resolve => setTimeout(resolve, 1600));

                    return timeout.then(() => check(callId));
                }
                else {
                    return data;
                }
            });
        };

        const requestBody = {
            'prompt': prompt.text,
            'seed': seed,
            'latents': latents?.tensor,
            'timestep': timestep,
            'trajectory_at': trajectoryAt,
        };
        const requestArgs = {
            'signature': latents?.signature ?? prompt.signature,
        };
        const request = this.post(
            '/diffusions',
            requestBody,
            {
                args: requestArgs,
                signal: abort.signal,
            },
        )
        .then((data) => {
            if(data['call_id'] !== undefined) {
                return check(data['call_id'], abort.signal);
            }
            else {
                return data;
            }
        })
        .then((data) => {
            return {
                image: data['diffusion']['image'],
                trajectory: new Map(
                    data['diffusion']['trajectory'].map(
                        info => [
                            info['timestep'],
                            {
                                ...info,
                                signature: data['signatures'][info['timestep']],
                            },
                        ],
                    ),
                ),
            }
        });

        return { abort, request };
    }
}
