let multipleUpload = function (model, oldFiles, maxFiles, maxSize, allowedTypes, translatedAttribute, translatedFormats) {
    return {
        oldFiles: oldFiles || [],
        files: [],
        items: [],
        dragging: false,
        model: model,
        uploadLength: 0,
        maxFiles: maxFiles,
        maxSize: maxSize,
        allowedTypes: allowedTypes,
        translatedAttribute: translatedAttribute,
        translatedFormats: translatedFormats,
        init() {
            this.oldFiles = this.oldFiles || [];

            if (this.oldFiles.length > 0) {
                this.oldFiles = this.oldFiles.map(file => ({
                    id: file.id,
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    preview: file.preview,
                    progress: 100
                }));
            }
        },
        handleDrop(files) {
            this.dragging = false;
            $refs.input.files = files;
            $refs.input.dispatchEvent(new Event('change', {bubbles: true}));
        },
        addFiles(files) {
            this.$dispatch('clear-validation-errors');

            if (!this.checkAllFilesIsValid(files)) {
                return;
            }

            for (const file of files) {
                this.files.push({
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    key: `${Date.now()}-${Math.floor(Math.random() * 100000)}`,
                    preview: URL.createObjectURL(file),
                    progress: 0
                });
            }

            if (files.length === 0) return;

            this.items = [...this.items, ...files];

            this.uploadLength = files.length;

            this.$wire.uploadMultiple(this.model, this.items, () => {}, () => {}, (event) => {
                this.handleUploadProgress(event.detail.progress);
            });
        },
        checkAllFilesIsValid(files) {
            if (!this.validateMaxFiles(files)) {
                return false;
            }

            for (const file of files) {
                if (!this.validateFileType(file) || !this.validateFileSize(file)) {
                    return false;
                }
            }

            return true;
        },
        validateMaxFiles(files) {
            if (this.oldFiles.length + this.items.length + files.length > this.maxFiles) {
                this.$dispatch('validation-error-alert', {
                    model: this.model,
                    message: `O campo ${this.translatedAttribute} deve conter no máximo ${this.maxFiles} arquivos.`,
                });

                return false;
            }

            return true;
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
        handleUploadProgress(globalProgress) {
            const slice = 100 / (this.uploadLength + this.files.length)

            const completeCount = Math.floor(globalProgress / slice);

            for (let i = 0; i < completeCount; i++) {
                if (this.files[i]) this.files[i].progress = 100;
            }

            if (this.files[completeCount]) {
                const localProgress = ((globalProgress - (completeCount * slice)) / slice) * 100;
                this.files[completeCount].progress = Math.round(localProgress);
            }

            for (let i = completeCount + 1; i < this.files.length; i++) {
                if (this.files[i]) this.files[i].progress = 0;
            }
        },
        removeFile(index, oldFile = false) {
            if (oldFile) {
                const file = this.oldFiles[index];
                this.oldFiles.splice(index, 1);
                this.$wire.dispatch('remove::file', {mediaId: file.id});

                return;
            }

            this.files.splice(index, 1);
            this.items.splice(index, 1);

            const temp = $wire.get(this.model)[index].replace('livewire-file:', '');
            $wire.removeUpload(this.model, temp);
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
        getPreviewId(prefix, type, index) {
            return `${prefix}-${type}-preview-${index}`;
        }
    }
};

export default multipleUpload;
