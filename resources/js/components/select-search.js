let selectSearch = function (t) {
    return {
        init(element) {
            this.element = element;

            this.getOptions()
                .then((data) => {
                    this.items = data;
                })
                .finally(() => {
                    this.loading = false;
                });

            this.$watch("activeIndex", () => {
                this.open &&
                    (null !== this.activeIndex
                        ? (this.activeDescendant =
                              this.$refs.ul.children[this.activeIndex].id)
                        : (this.activeDescendant = ""));
            });

            this.$watch("value", (value, oldValue) => {
                if (!value) {
                    this.selectedIndex = null;
                    this.search = null;

                    this.getOptions()
                        .then((data) => {
                            this.items = data;

                            this.selectedItem = {
                                id: null,
                                name: this.defaultOptionLabel,
                            };
                        })
                        .finally(() => {
                            this.loading = false;
                        });
                } else if (
                    value &&
                    value !== oldValue &&
                    !this.isLoadingOptions
                ) {
                    // Verifica se o item já está na lista antes de recarregar
                    const itemExists = this.items.find(
                        (s) => s.id.toString() === value.toString()
                    );

                    if (itemExists) {
                        // Item já está na lista, apenas seleciona
                        this.selectedItem = itemExists;
                        this.selectedIndex = this.items.findIndex(
                            (s) => s.id.toString() === value.toString()
                        );
                        return;
                    }

                    // Item não está na lista, precisa recarregar
                    this.isLoadingOptions = true;
                    this.loading = true;

                    this.getOptions()
                        .then((data) => {
                            this.items = data;

                            // Encontra e define o item selecionado
                            const foundItem = this.items.find(
                                (s) => s.id.toString() === value.toString()
                            );

                            if (foundItem) {
                                this.selectedItem = foundItem;
                                this.selectedIndex = this.items.findIndex(
                                    (s) => s.id.toString() === value.toString()
                                );
                            }
                        })
                        .catch((error) => {
                            console.error("Failed to load options:", error);
                        })
                        .finally(() => {
                            this.loading = false;
                            this.isLoadingOptions = false;
                        });
                }

                this.$nextTick(() => {});
            });

            this.$watch("items", (newItems) => {
                this.$nextTick(() => {
                    this.forceUpdate();
                });
            });

            // Adiciona listeners para recalcular posição do dropdown
            this.$nextTick(() => {
                window.addEventListener("resize", () => {
                    if (this.open) this.checkDropdownPosition();
                });
                window.addEventListener(
                    "scroll",
                    () => {
                        if (this.open) this.checkDropdownPosition();
                    },
                    true
                );
            });
        },
        element: null,
        initialValue: null,
        selectedItem: null,
        value: null,
        withInfinityScroll: true,
        open: false,
        name: null,
        loading: true,
        isLoadingOptions: false,
        route: null,
        items: [],
        activeIndex: null,
        selectedIndex: null,
        activeDescendant: null,
        wireModel: null,
        wire: null,
        search: null,
        defaultOptionLabel: "Selecione uma opção",
        selectedColumn: "id",
        isLive: false,
        dropdownUp: false,
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
            },
            links: {
                first: null,
                last: null,
                next: null,
            },
        },
        get optionCount() {
            return this.items.length;
        },
        get selected() {
            if (!this.value || this.value === null || this.value === "") {
                const defaultItem = {
                    id: null,
                    name: this.defaultOptionLabel,
                };

                this.selectedItem = defaultItem;
                return defaultItem;
            }

            if (this.loading) {
                let name =
                    this.initialValue ||
                    this.selectedItem?.name ||
                    this.defaultOptionLabel ||
                    "Selecione uma opção";

                const loadingItem = {
                    id: this.value,
                    name: name,
                };

                this.selectedItem = loadingItem;
                return loadingItem;
            }

            this.selectedIndex = this.items.findIndex(
                (s) => s.id.toString() === this.value.toString()
            );
            let foundItem = this.items.find(
                (s) => s.id.toString() === this.value.toString()
            );

            if (foundItem) {
                this.selectedItem = foundItem;
                return foundItem;
            }

            return (
                this.selectedItem || {
                    id: this.value,
                    name: this.defaultOptionLabel,
                }
            );
        },
        async getOptions(page = null) {
            let url = this.route;

            if (page) {
                url += url.includes("?") ? "&" : "?";
                url += new URLSearchParams({ page: page });
            }

            if (this.search) {
                url += url.includes("?") ? "&" : "?";
                url += new URLSearchParams({ search: this.search });
            }

            url += url.includes("?") ? "&" : "?";
            url += new URLSearchParams({ selectedColumn: this.selectedColumn });

            if (this.value) {
                url += url.includes("?") ? "&" : "?";
                url += `selected[]=${encodeURIComponent(this.value)}`;
            }

            let response = await fetch(url);
            let json = await response.json();

            let { meta, links, data } = json;

            this.data = { meta, links };

            return data;
        },
        async infinityScroll() {
            if (!this.withInfinityScroll) {
                return;
            }

            if (this.data.links?.next !== null) {
                let scroll = this.$refs.ul.scrollTop;
                let scrollHeight = this.$refs.ul.scrollHeight;
                let clientHeight = this.$refs.ul.clientHeight;

                if (scroll + 10 >= scrollHeight - clientHeight) {
                    this.loading = true;
                    await this.loadMore();
                }
            }
        },
        async loadMore() {
            try {
                let data = await this.getOptions(
                    this.data.meta.current_page + 1
                );
                this.items = [...this.items, ...data];
            } catch (error) {
                console.error("Failed to load more:", error);
            } finally {
                this.loading = false;
            }
        },
        async doSearch() {
            this.loading = true;

            try {
                this.items = await this.getOptions();

                this.$nextTick(() => {
                    this.activeIndex = this.items.length > 0 ? 0 : null;

                    this.forceUpdate();
                });
            } catch (error) {
                console.error("Search failed:", error);
            } finally {
                this.loading = false;
            }
        },
        openList() {
            if (this.open) {
                this.open = false;
                this.activeIndex = null;
                return;
            }

            this.checkDropdownPosition();
            this.open = true;

            this.$nextTick(() => {
                if (this.withSearch) {
                    this.$refs.search.focus();
                }

                let index = this.items.findIndex(
                    (s) =>
                        s.id.toString() ===
                        (this.selectedItem?.id
                            ? this.selectedItem.id.toString()
                            : null)
                );

                // Inicializa activeIndex com o item selecionado ou primeiro item
                if (index >= 0) {
                    this.activeIndex = index;
                } else if (this.items.length > 0) {
                    this.activeIndex = 0;
                }

                this.$refs.ul.children[index]?.scrollIntoView({
                    block: "center",
                });

                this.$refs.searchBox.style.width =
                    this.element.offsetWidth + "px";
            });

            function onResize(searchBox, element) {
                searchBox.style.width = element.offsetWidth + "px";
            }

            window.onresize = () =>
                onResize(this.$refs.searchBox, this.element);
        },

        selectSearchFocus() {
            this.$refs.ul.focus();

            if (this.selectedItem?.id) {
                let index = this.items.findIndex(
                    (s) => s.id.toString() === this.selectedItem.id.toString()
                );

                if (index >= 0) {
                    this.activeIndex = index;
                    this.$refs.ul.children[index]?.scrollIntoView({
                        block: "nearest",
                    });
                }
            } else if (this.items.length > 0) {
                this.activeIndex = 0;
            }
        },
        onEscape() {
            this.open = false;
            this.activeIndex = null;
            this.$refs.button.focus();
        },
        choose(t) {
            this.selectedIndex = t;
            this.open = false;
            this.activeIndex = null;
            this.selectedItem = this.items[this.selectedIndex];
            this.value = this.selectedItem["id"];

            this.$wire.set(
                this.wireModel,
                this.selectedItem["id"],
                this.isLive
            );

            this.$nextTick(() => {});
        },
        forceUpdate() {
            this.$nextTick(() => {});
        },
        resetState() {
            this.selectedIndex = null;
            this.activeIndex = null;
            this.search = null;
            this.open = false;

            this.selectedItem = {
                id: null,
                name: this.defaultOptionLabel,
            };

            this.getOptions().then((data) => {
                this.items = data;
                this.forceUpdate();
            });
        },
        remove() {
            this.selectedIndex = null;
            this.open = false;

            this.$wire.set(this.wireModel, null, this.isLive);

            this.value = null;
            this.selectedItem = {
                id: null,
                name: this.defaultOptionLabel,
            };

            this.$nextTick(() => {
                this.getOptions().then((data) => {
                    this.items = data;
                });
            });
        },
        checkDropdownPosition() {
            const button = this.$refs.button;
            const dropdown = this.$refs.searchBox;

            if (!button || !dropdown) return;

            const buttonRect = button.getBoundingClientRect();
            const dropdownHeight = 240; // max-h-60 aproximadamente
            const viewportHeight = window.innerHeight;
            const spaceBelow = viewportHeight - buttonRect.bottom;
            const spaceAbove = buttonRect.top;

            // Se não há espaço suficiente abaixo mas há espaço acima, mostra para cima
            this.dropdownUp = spaceBelow < dropdownHeight && spaceAbove > dropdownHeight;
        },
        onOptionSelect() {
            null !== this.activeIndex &&
                (this.selectedIndex = this.activeIndex);
            this.$refs.button.focus();
            this.choose(this.activeIndex);
        },
        onArrowUp() {
            if (this.activeIndex === null) {
                this.activeIndex = this.items.length - 1;
            } else if (this.activeIndex > 0) {
                this.activeIndex--;
            }

            // Scroll imediatamente - pega apenas os <li>
            const listItems = this.$refs.ul.querySelectorAll('li[role="option"]');
            if (this.activeIndex !== null && listItems[this.activeIndex]) {
                const activeElement = listItems[this.activeIndex];
                const container = this.$refs.ul;

                const elementRect = activeElement.getBoundingClientRect();
                const containerRect = container.getBoundingClientRect();

                if (elementRect.top < containerRect.top) {
                    container.scrollTop -= containerRect.top - elementRect.top;
                }

                // Se voltou para o índice 0, garante que está no topo
                if (this.activeIndex === 0) {
                    container.scrollTop = 0;
                }

                if (this.activeIndex === this.items.length - 1) {
                    container.scrollTop = container.scrollHeight;
                }
            }

            // Verifica se precisa carregar mais itens
            this.infinityScroll();
        },
        onArrowDown() {
            if (this.activeIndex === null) {
                this.activeIndex = 0;
            } else if (this.activeIndex < this.items.length - 1) {
                this.activeIndex++;
            }

            // Scroll imediatamente - pega apenas os <li>
            const listItems = this.$refs.ul.querySelectorAll('li[role="option"]');
            if (this.activeIndex !== null && listItems[this.activeIndex]) {
                const activeElement = listItems[this.activeIndex];
                const container = this.$refs.ul;

                const elementRect = activeElement.getBoundingClientRect();
                const containerRect = container.getBoundingClientRect();

                if (elementRect.bottom > containerRect.bottom) {
                    const scrollAmount = elementRect.bottom - containerRect.bottom;
                    container.scrollTop += scrollAmount;
                }

                if (this.activeIndex === 0) {
                    container.scrollTop = 0;
                }

                if (this.activeIndex === this.items.length - 1) {
                    container.scrollTop = container.scrollHeight;
                }
            }

            // Verifica se precisa carregar mais itens
            this.infinityScroll();
        },
        scrollToActiveItem() {
            // Função mantida para compatibilidade, mas o scroll agora é feito diretamente nas funções de seta
        },
        ...t,
    };
};

export default selectSearch;
