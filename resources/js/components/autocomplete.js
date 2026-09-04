let autocomplete = function (t) {
    return {
        element: null,
        initialValue: null,
        selectedItem: null,
        value: null,
        withInfinityScroll: true,
        open: false,
        name: null,
        route: null,
        items: [],
        wireModel: null,
        wire: null,
        search: null,
        isLive: false,
        activeDescendant: null,
        selectedColumn: 'id',
        loading: false,
        focus: false,
        oldValue: null,
        data: {
            meta: {
                current_page: null,
                from: null,
                last_page: null,
                links: {},
                path: null,
                per_page: null,
                to: null,
                total: null,
            }, links: {
                first: null, last: null, next: null
            }
        },
        init(element) {
            this.element = element;

            this.$watch('value', (value) => {
                if (!value || value.length <= 1) {
                    this.open = false;
                    this.items = [];
                    return;
                }

                this.open = true;
                this.getOptions().then(data => {
                    this.items = data;
                });
            });
        },
        async getOptions(page = null) {
            this.loading = true;

            let url = this.route;

            if (page) {
                url += url.includes('?') ? '&' : '?';
                url += new URLSearchParams({page: page});
            }

            if (this.value) {
                url += url.includes('?') ? '&' : '?';
                url += new URLSearchParams({search: this.value});
            }

            let response = await fetch(url);
            let json = await response.json();

            let {meta, links, data} = json;

            this.data = {meta, links};
            this.loading = false;

            return data;
        },
        onFocus() {
            this.focus = true;
            this.open = true;
        },
        choose(index) {
            this.value = this.items[index].name;
            this.setWireValue()
            this.open = false;
        },
        close() {
            if (this.focus || this.open) {
                this.setWireValue()
            }

            this.open = false;
        },
        setWireValue() {
            if (this.oldValue !== this.value) {
                this.oldValue = this.value;
                this.$wire.set(this.wireModel, this.value);
            }
        },
        ...t,
    }
};

export default autocomplete;
