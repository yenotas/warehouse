// Функция масштабирования изображения
window.resizeImage = function(file, maxHeight, callback) {
    var reader = new FileReader();
    reader.onload = function(event) {
        var img = new Image();
        img.onload = function() {
            var ratio = maxHeight / img.height;
            var newWidth = img.width * ratio;
            var newHeight = img.height * ratio;

            var canvas = document.createElement('canvas');
            canvas.width = newWidth;
            canvas.height = newHeight;

            var ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, newWidth, newHeight);
            ctx.drawImage(img, 0, 0, newWidth, newHeight);

            canvas.toBlob(function(blob) {
                var resizedFile = new File([blob], file.name || "pasted_image.png", {
                    type: file.type || "image/png",
                    lastModified: Date.now()
                });
                callback(resizedFile, canvas.toDataURL(file.type || "image/png"));
            }, file.type || "image/png");
        };
        img.src = event.target.result;
    };
    reader.readAsDataURL(file);
}

// Преобразование base64 в Blob
window.base64ToBlob = function(base64, mime) {
    mime = mime || 'image/png';
    var byteString = atob(base64.split(',')[1]);
    var ab = new ArrayBuffer(byteString.length);
    var ia = new Uint8Array(ab);
    for (var i = 0; i < byteString.length; i++) {
        ia[i] = byteString.charCodeAt(i);
    }
    var file = null;
    var blob = new Blob([ab], { type: mime });
    if (blob) {
        console.log('файл конвертирован base64ToBlob');
        file = new File([blob], "uploaded_image.png", { type: mime });
    }
    return file;
}

// Обработка вставки HTML-кода с изображением в формате base64
window.getImageFromHTML = function(item, callback) {
    item.getAsString(function(str) {
        console.log('разбираем ряд', str);
        // Поиск тега <img> с атрибутом src
        var match = str.match(/<img[^>]+src="([^"]+)"/);
        var file = null;
        if (match && match[1].startsWith('data:image/')) {
            var dataURL = match[1];
            var mimeString = dataURL.split(',')[0].split(':')[1].split(';')[0];
            console.log('найден файл', mimeString);
            var file = base64ToBlob(dataURL, mimeString);
            if (file) {
                console.log('файл обработан!');
            }
        }
        callback(file);
    });
};


// Инициализация ячейки
class ImageCell {
    constructor(img_cell) {
        this.img_cell = img_cell;
        this.imagePreviewContainer = img_cell.find('.image_preview_container');
        this.imagePreview = img_cell.find('.image_preview');
        this.removeImageButton = img_cell.find('.remove_image_button');
        this.imagePasteArea = img_cell.find('.image_paste_area');
        this.imagePasteAreaBG = img_cell.find('.image_paste_area_bg');
        this.productImageInput = img_cell.find('.product_image');
        this.initEvents();
    }

    initEvents() {
        this.imagePasteArea.on('paste', this.handlePaste.bind(this));
        this.removeImageButton.on('click', this.handleRemove.bind(this));
        this.imagePreviewContainer.on('dblclick', this.handleDoubleClick.bind(this));
    }

    handlePaste(event) {
        var items = (event.originalEvent.clipboardData || event.clipboardData).items;

        for (var i = 0; i < items.length; i++) {
            var item = items[i];
            if (item.kind === 'file') {
                var file = item.getAsFile();
                if (file) {
                    this.insertImage(file);
                    console.log('Изображение вставлено из файла');
                    break;
                }
            } else if (item.kind === 'string') {
                getImageFromHTML(item, (file) => {
                    if (file) {
                        this.insertImage(file);
                        console.log('Изображение вставлено из HTML-кода');
                    }
                });
            }
        }

        setTimeout(() => {
            this.imagePasteArea.html('');
        }, 50);
    }

    handleRemove(event) {
        event.preventDefault();
        this.imagePreview.hide();
        this.removeImageButton.hide();
        this.productImageInput.val('');
        this.imagePasteAreaBG.show();
        this.imagePasteArea.show();
    }

    handleDoubleClick(event) {
        this.productImageInput.click();
    }

    insertImage(file) {
        resizeImage(file, 500, (resizedFile, dataURL) => {
            var container = new DataTransfer();
            container.items.add(resizedFile);
            this.productImageInput[0].files = container.files;
            this.imagePreview.attr('src', dataURL);
            this.imagePasteAreaBG.hide();
            this.imagePreview.show();
            this.imagePasteArea.hide();
            this.removeImageButton.show();
        });
    }
}

window.initializeCell = function(img_cell) {
    new ImageCell(img_cell);
}

django.jQuery(document).ready(function($) {
    $('.img_cell').each(function() {
        initializeCell($(this));
    });
});
