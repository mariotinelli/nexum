let multiSelectSearch = function (t) {
    return {
        init(element) {
            this.element = element;
            this.getOptions().then((data) => {
                this.items = data;
                if (this.value?.length) {
                    this.selectedItems = this.value.map((id) => id.toString());
                }

                this.$watch('value', (value) => {
                    this.selectedItems = Array.isArray(value)
                        ? value.map((id) => id.toString())
                        : [];
                });
            });

            this.$watch("activeIndex", () => {
                this.open &&
                    (null !== this.activeIndex
                        ? (this.activeDescendant =
                              this.$refs.ul.children[this.activeIndex].id)
                        : (this.activeDescendant = ""));
            });

            // Adiciona listeners para recalcular posição do dropdown
            this.$nextTick(() => {
                window.addEventListener('resize', () => { 
                    if (this.open) this.checkDropdownPosition(); 
                });
                window.addEventListener('scroll', () => { 
                    if (this.open) this.checkDropdownPosition(); 
                }, true);
            });
        },
        activeDescendant: null,
        activeIndex: null,
        element: null,
        initialValue: [],
        selectedItems: [],
        value: null,
        withInfinityScroll: true,
        open: false,
        name: null,
        loading: true,
        route: null,
        items: [],
        search: null,
        withSearch: null,
        selectedColumn: 'id',
        defaultOptionLabel: "Selecione uma ou mais opções",
        isLive: false,
        dropdownUp: false,
        get optionCount() {
            return this.filteredItems.length;
        },
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
        get selected() {
            if (this.selectedItems.length === 0) {
                return [{ id: null, name: this.defaultOptionLabel }];
            }

            return this.items.filter((item) =>
                this.selectedItems.includes(item.id.toString())
            );
        },
        get filteredItems() {
            return this.items.filter(
                (item) => !this.selectedItems.includes(item.id.toString())
            );
        },
        async getOptions(route = null) {
            let url = route || this.route;
            if (this.search) {
                url += url.includes("?") ? "&" : "?";
                url += new URLSearchParams({ search: this.search });
            }

            url += url.includes("?") ? "&" : "?";
            url += new URLSearchParams({ selectedColumn: this.selectedColumn });

            if (this.value?.length) {
                url += url.includes("?") ? "&" : "?";
                url += this.value.map(id => `selected[]=${encodeURIComponent(id)}`).join("&");
            }

            let response = await fetch(url);
            let json = await response.json();

            let {meta, links, data} = json;
            this.data = {meta, links};

            this.loading = false;
            return data;
        },
        choose(index) {
            const item = this.filteredItems[index];

            if (!item) {
                return;
            }

            if (this.selectedItems.includes(item.id.toString())) {
                this.selectedItems = this.selectedItems.filter((id) => id !== item.id.toString());
            } else {
                this.selectedItems.push(item.id.toString());
            }

            this.$wire.set(this.wireModel, [...this.selectedItems], this.isLive);
        },
        isSelected(index) {
            const item = this.filteredItems[index];

            if (!item) {
                return false;
            }

            return this.selectedItems.includes(item.id.toString());
        },
        remove(itemId) {
            this.selectedItems = this.selectedItems.filter((id) => id !== itemId.toString());
            this.$wire.set(this.wireModel, [...this.selectedItems], this.isLive);
        },
        async doSearch() {
            this.items = await this.getOptions();
        },
        async infinityScroll() {
            if (!this.withInfinityScroll) {
                return;
            }

            if (this.data.links?.next !== null) {
                let scroll = this.$refs.multiSelectSearchBox.scrollTop;
                let scrollHeight = this.$refs.multiSelectSearchBox.scrollHeight;
                let clientHeight = this.$refs.multiSelectSearchBox.clientHeight;

                if (scroll >= (scrollHeight - clientHeight)) {
                    this.loading = true;
                    await this.loadMore();
                }
            }
        },
        async loadMore() {
            let data = await this.getOptions(this.data.links?.next);
            this.items = [...this.items, ...data];
        },
        openList() {
            this.checkDropdownPosition();
            this.open = !this.open;

            this.$nextTick(() => {
                if (this.withSearch) {
                    this.$refs.search.focus();
                } else {
                    this.$refs.ul?.focus();
                }

                // Inicializa activeIndex no primeiro item
                if (this.open && this.filteredItems.length > 0) {
                    this.activeIndex = 0;
                }

                this.$refs.multiSelectSearchBox.style.width = this.element.offsetWidth + "px";
            });
        },
        checkDropdownPosition() {
            const button = this.$refs.button;
            const dropdown = this.$refs.multiSelectSearchBox;
            
            if (!button || !dropdown) return;
            
            const buttonRect = button.getBoundingClientRect();
            const dropdownHeight = 250; // max-h-60 aproximadamente
            const viewportHeight = window.innerHeight;
            const spaceBelow = viewportHeight - buttonRect.bottom;
            const spaceAbove = buttonRect.top;
            
            // Se não há espaço suficiente abaixo mas há espaço acima, mostra para cima
            this.dropdownUp = spaceBelow < dropdownHeight && spaceAbove > dropdownHeight;
        },
        onEscape() {
            this.open = false;
            this.activeIndex = null;
            this.$refs.button.focus();
        },
        onOptionSelect() {
            if (this.activeIndex !== null) {
                this.choose(this.activeIndex);
            }
        },
        onArrowUp() {
            if (this.activeIndex === null) {
                this.activeIndex = this.filteredItems.length - 1;
            } else if (this.activeIndex > 0) {
                this.activeIndex--;
            }

            // Scroll imediatamente - pega apenas os <li>
            const listItems = this.$refs.ul.querySelectorAll('li[role="option"]');
            if (this.activeIndex !== null && listItems[this.activeIndex]) {
                const activeElement = listItems[this.activeIndex];
                const container = this.$refs.multiSelectSearchBox;

                const elementRect = activeElement.getBoundingClientRect();
                const containerRect = container.getBoundingClientRect();

                if (elementRect.top < containerRect.top) {
                    container.scrollTop -= containerRect.top - elementRect.top;
                }

                // Se voltou para o índice 0, garante que está no topo
                if (this.activeIndex === 0) {
                    container.scrollTop = 0;
                }

                if (this.activeIndex === this.filteredItems.length - 1) {
                    container.scrollTop = container.scrollHeight;
                }
            }

            // Verifica se precisa carregar mais itens
            this.infinityScroll();
        },
        onArrowDown() {
            if (this.activeIndex === null) {
                this.activeIndex = 0;
            } else if (this.activeIndex < this.filteredItems.length - 1) {
                this.activeIndex++;
            }

            // Scroll imediatamente - pega apenas os <li>
            const listItems = this.$refs.ul.querySelectorAll('li[role="option"]');
            if (this.activeIndex !== null && listItems[this.activeIndex]) {
                const activeElement = listItems[this.activeIndex];
                const container = this.$refs.multiSelectSearchBox;

                const elementRect = activeElement.getBoundingClientRect();
                const containerRect = container.getBoundingClientRect();

                if (elementRect.bottom > containerRect.bottom) {
                    const scrollAmount = elementRect.bottom - containerRect.bottom;
                    container.scrollTop += scrollAmount;
                }

                if (this.activeIndex === 0) {
                    container.scrollTop = 0;
                }

                if (this.activeIndex === this.filteredItems.length - 1) {
                    container.scrollTop = container.scrollHeight;
                }
            }

            // Verifica se precisa carregar mais itens
            this.infinityScroll();
        },
        ...t,
    };
};

export default multiSelectSearch;
