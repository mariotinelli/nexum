let multiSelect = function (t) {
    return {
        activeDescendant: null,
        open: false,
        activeIndex: null,
        initialValue: [],
        selectedItems: [],
        defaultOptionLabel: "Selecione uma ou mais opções",
        items: [],
        remainingOptions: [],
        value: null,
        isLive: false,
        dropdownUp: false,
        get optionCount() {
            return this.filteredItems.length;
        },
        init() {
            this.formatItems();

            if (this.value?.length) {
                this.selectedItems = this.value.map((id) => id.toString());
            }

            this.$watch("activeIndex", () => {
                this.open &&
                    (null !== this.activeIndex
                        ? (this.activeDescendant =
                              this.$refs.ul.children[this.activeIndex].id)
                        : (this.activeDescendant = ""));
            });

            this.$watch("value", (value) => {
                this.selectedItems = Array.isArray(value)
                    ? value.map((id) => id.toString())
                    : [];
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
            return this.filteredItems[this.activeIndex];
        },
        get filteredItems() {
            return this.items.filter(
                (item) => !this.selectedItems.includes(item.id.toString())
            );
        },
        get selected() {
            if (this.selectedItems.length === 0) {
                return [{ id: null, name: this.defaultOptionLabel }];
            }

            return this.items.filter((item) =>
                this.selectedItems.includes(item.id.toString())
            );
        },
        choose(index) {
            const item = this.filteredItems[index];

            if (!item) {
                return;
            }

            if (this.selectedItems.includes(item.id.toString())) {
                this.selectedItems = this.selectedItems.filter(
                    (id) => id !== item.id.toString()
                );
            } else {
                this.selectedItems.push(item.id.toString());
            }

            this.$wire.set(
                this.wireModel,
                [...this.selectedItems],
                this.isLive
            );
        },
        remove(itemId) {
            this.selectedItems = this.selectedItems.filter(
                (id) => id !== itemId.toString()
            );
            this.$wire.set(
                this.wireModel,
                [...this.selectedItems],
                this.isLive
            );
        },
        removeAll() {
            this.selectedItems = [];
            this.$wire.set(
                this.wireModel,
                [...this.selectedItems],
                this.isLive
            );
        },
        onButtonClick() {
            this.checkDropdownPosition();
            this.open = !this.open;
            this.$nextTick(() => {
                if (this.open) {
                    this.$refs.ul?.focus();
                    
                    // Inicializa activeIndex no primeiro item
                    if (this.filteredItems.length > 0) {
                        this.activeIndex = 0;
                    }

                    const listItems = this.$refs.ul?.querySelectorAll('li[role="option"]');
                    if (this.activeIndex !== null && listItems?.[this.activeIndex]) {
                        listItems[this.activeIndex].scrollIntoView({
                            block: "center",
                        });
                    }
                }
            });
        },
        checkDropdownPosition() {
            const button = this.$refs.button;
            const dropdown = this.$refs.selectMultipleBox;

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
                this.activeIndex = this.filteredItems.length - 1;
            } else if (this.activeIndex > 0) {
                this.activeIndex--;
            }

            // Scroll imediatamente - pega apenas os <li>
            const listItems = this.$refs.ul.querySelectorAll('li[role="option"]');
            if (this.activeIndex !== null && listItems[this.activeIndex]) {
                const activeElement = listItems[this.activeIndex];
                const container = this.$refs.selectMultipleBox;

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
                const container = this.$refs.selectMultipleBox;

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
        },
        isSelected(index) {
            const item = this.items[index];
            return this.selectedItems.includes(item.id.toString());
        },
        getSelectedNames() {
            return this.selected()
                .map((item) => item.name)
                .join(", ");
        },
        ...t,
    };
};

export default multiSelect;
