let select = function (t) {
    return {
        init() {
            this.optionCount = this.$refs.selectBox.children.length;
            this.formatItems();

            this.$watch("activeIndex", () => {
                this.open &&
                    (null !== this.activeIndex
                        ? (this.activeDescendant =
                              this.$refs.ul.children[this.activeIndex].id)
                        : (this.activeDescendant = ""));
            });

            this.$watch("value", (value) => {
                if (!value) {
                    this.selectedItem = {
                        id: null,
                        name: this.defaultOptionLabel,
                    };

                    this.selectedIndex = null;
                }
            });

            this.$wire.on("refresh::options", (event) => {
                if (event.model === this.wireModel) {
                    this.items = event.options;
                    this.formatItems();
                }
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
        activeDescendant: null,
        optionCount: null,
        open: !1,
        activeIndex: null,
        selectedIndex: null,
        defaultOptionLabel: "Selecione uma opção",
        items: [],
        value: null,
        clearable: true,
        isLive: false,
        dropdownUp: false,
        formatItems() {
            if (Array.isArray(this.items)) {
                return;
            }

            this.items = Object.entries(this.items).map(([key, value]) => {
                return {
                    id: key,
                    name: value,
                };
            });
        },
        get active() {
            return this.items[this.activeIndex];
        },
        get selected() {
            if (!this.value || this.items.length === 0) {
                return {
                    id: null,
                    name: this.defaultOptionLabel,
                };
            }

            this.selectedIndex = this.items.findIndex(
                (s) => s.id.toString() === this.value.toString()
            );

            if (this.selectedIndex === -1) {
                return {
                    id: null,
                    name: this.defaultOptionLabel,
                };
            }

            return this.items.find(
                (s) => s.id.toString() === this.value.toString()
            );
        },
        choose(t) {
            if (this.selectedIndex === t) {
                if (!this.clearable) {
                    return;
                }

                this.selectedIndex = null;
                this.open = false;
                this.$wire.set(this.wireModel, null, this.isLive);
                return;
            }

            this.selectedIndex = t;
            this.open = false;
            this.value = this.items[this.selectedIndex]["id"];
            this.$wire.set(this.wireModel, this.items[this.selectedIndex]["id"], this.isLive);
        },
        remove() {
            this.selectedIndex = null;
            this.open = false;
            this.selectedItem = {
                id: null,
                name: this.defaultOptionLabel,
            };
            this.$wire.set(this.wireModel, null, this.isLive);
        },
        onButtonClick() {
            this.openList();
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
                this.$refs.ul.focus();

                // Inicializa activeIndex com o item selecionado ou primeiro item
                if (this.selectedIndex !== null && this.selectedIndex >= 0) {
                    this.activeIndex = this.selectedIndex;
                } else if (this.items.length > 0) {
                    this.activeIndex = 0;
                }

                const listItems = this.$refs.ul.querySelectorAll('li[role="option"]');
                if (this.activeIndex !== null && listItems[this.activeIndex]) {
                    listItems[this.activeIndex].scrollIntoView({
                        block: "center",
                    });
                }
            });
        },
        checkDropdownPosition() {
            const button = this.$refs.button;
            const dropdown = this.$refs.selectBox;

            if (!button || !dropdown) return;

            const buttonRect = button.getBoundingClientRect();
            const dropdownHeight = 224; // max-h-56 aproximadamente
            const viewportHeight = window.innerHeight;
            const spaceBelow = viewportHeight - buttonRect.bottom;
            const spaceAbove = buttonRect.top;

            // Se não há espaço suficiente abaixo mas há espaço acima, mostra para cima
            this.dropdownUp =
                spaceBelow < dropdownHeight && spaceAbove > dropdownHeight;
        },
        onOptionSelect() {
            if (this.activeIndex !== null) {
                this.choose(this.activeIndex);
            }
        },
        onEscape() {
            this.open = false;
            this.activeIndex = null;
            this.$refs.button.focus();
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
        },
        ...t,
    };
};

export default select;
