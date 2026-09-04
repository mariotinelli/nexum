export default (isLive, wireModel, model, config) => ({
    isLive: isLive,
    wireModel: wireModel,
    model: model,
    config: config,
    pickr: null,

    init() {
        this.pickr = flatpickr(this.$refs.datepicker, this.config)

        this.pickr.setDate(this.model);

        this.$watch('model', (value) => {
            this.$wire.set(this.wireModel, value, this.isLive);
        });
    },
    openCalendar() {
        this.pickr.open()
    }
});
