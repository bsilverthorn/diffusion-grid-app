export class DGAPI {
    constructor(apiRoot, errorListener) {
        this.apiRoot = apiRoot;
        this.errorListener = errorListener;
    }

    call(method, path, data, options = {}) {
        return fetch(
            this.apiRoot + path,
            {
                method: method,
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
                ...options,
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
            if(error.name === 'AbortError') {
                console.log("aborted request to", path);
            }
            else {
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
}
