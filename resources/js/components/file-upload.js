let fileUpload = function (model, maxSize, allowedTypes, translatedAttribute, translatedFormats) {
    return {
        file: null,
        size: null,
        dragging: false,
        model: model,
        maxSize: maxSize,
        allowedTypes: allowedTypes,
        translatedAttribute: translatedAttribute,
        translatedFormats: translatedFormats,
        init(){
            const file = this.$wire.get(this.model);

            if (file) {
                this.file = {
                    id: file.id,
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    preview: file.preview,
                    progress: 100,
                    uploaded: false,
                    persisted: true
                };
            }
        },
        handleDrop(files){
            this.dragging = false;
            this.$refs.input.files = files;
            this.$refs.input.dispatchEvent(new Event('change', {bubbles: true}));
        },
        addFile(files){
            this.$dispatch('clear-validation-errors');

            if (!this.checkFileIsValid(files)) {
                return;
            }

            this.file = {
                name: files[0].name,
                size: files[0].size,
                type: files[0].type,
                preview: URL.createObjectURL(files[0]),
                progress: 0,
                uploaded: true,
                persisted: false
            };

            this.$wire.upload(this.model, files[0], () => {}, () => {}, (event) => {
                this.file.progress = event.detail.progress;
            });
        },
        checkFileIsValid(files) {
            return !(!this.validateFileType(files[0]) || !this.validateFileSize(files[0]));
        },
        validateFileType(file) {
            if (!this.allowedTypes.split(',').some(type => type.split('/')[0] === file.type.split('/')[0])) {
                this.$dispatch('validation-error-alert', {
                    model: this.model,
                    message: `O arquivo ${file.name} não é um tipo permitido para o campo ${this.translatedAttribute}.`,
                    description: 'Tipos permitidos: ' + this.translatedFormats,
                });

                return false;
            }

            return true;
        },
        validateFileSize(file) {
            if (file.size > this.maxSize * 1024) { // kb to bytes conversion
                this.$dispatch('validation-error-alert', {
                    model: this.model,
                    message: `O arquivo ${file.name} excede o tamanho máximo permitido de ${this.maxSize / 1024} MB para o campo ${this.translatedAttribute}.`,
                });

                return false;
            }

            return true;
        },
        removeFile(){
            if (this.file?.persisted) {
                this.$wire.set(this.model, null);
                this.file = null;

                return;
            }

            const temp = this.$wire.get(this.model);
            this.$wire.removeUpload(this.model, temp);
            this.file = null;
        },
        getPreviewMimeTypes(type) {
            if (type === 'image') {
                return ['png', 'gif', 'bmp', 'svg', 'jpg', 'jpeg', 'webp'];
            }

            if (type === 'video') {
                return ['wav', 'mp4', 'mov', 'avi', 'wmv', 'mp3', 'm4a', 'mpga', 'wma'];
            }

            if (type === 'document') {
                return ['pdf', 'doc', 'docx', 'application/pdf', 'application/msword', 'application/vnd.ms-word', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
            }

            return [];
        },
        getPreviewId(prefix, type) {
            return `${prefix}-${type}-preview`;
        }
    }
};

export default fileUpload;
