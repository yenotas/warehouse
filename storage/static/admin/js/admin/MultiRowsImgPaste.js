django.jQuery(document).ready(function($) {

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

    // Обработка вставки HTML-кода с изображением в формате base64
    window.getImageFromHTML = function(item, callback) {
        item.getAsString(function(str) {
            var match = str.match(/data:image\/(png|jpeg|jpg);base64,[^"]+/);
            if (match) {
                var base64Image = match[0];
                var byteString = atob(base64Image.split(',')[1]);
                var mimeString = base64Image.split(',')[0].split(':')[1].split(';')[0];

                var ab = new ArrayBuffer(byteString.length);
                var ia = new Uint8Array(ab);
                for (var i = 0; i < byteString.length; i++) {
                    ia[i] = byteString.charCodeAt(i);
                }

                var blob = new Blob([ab], { type: mimeString });
                var file = new File([blob], "pasted_image." + mimeString.split('/')[1], { type: mimeString });
                callback(file);
            } else {
                callback(null); // Если base64 не найдено
            }
        });
    }

    // Инициализация ячейки
    window.initializeCell = function(img_cell) {
        var imagePreviewContainer = img_cell.find('.image_preview_container');
        var imagePreview = img_cell.find('.image_preview');
        var removeImageButton = img_cell.find('.remove_image_button');
        var imagePasteArea = img_cell.find('.image_paste_area');
        var imagePasteAreaBG = img_cell.find('.image_paste_area_bg');
        var productImageInput = img_cell.find('.product_image');

        function insertImage(file) {
            resizeImage(file, 50, function(resizedFile, dataURL) {
                var container = new DataTransfer();
                container.items.add(resizedFile);
                productImageInput[0].files = container.files;
                imagePreview.attr('src', dataURL);
                imagePasteAreaBG.hide();
                imagePreview.show();
                imagePasteArea.hide();
                removeImageButton.show();
            });
        }

        imagePasteArea.on('paste', function(event) {
            var items = (event.originalEvent.clipboardData || event.clipboardData).items;

            for (var i = 0; i < items.length; i++) {
                var item = items[i];
                if (item.kind === 'file') {
                    var file = item.getAsFile();
                    if (file) {
                        insertImage(file);
                        console.log('Изображение вставлено из файла');
                        break;
                    }
                } else if (item.kind === 'string') {
                    getImageFromHTML(item, function(file) {
                        if (file) {
                            insertImage(file);
                            console.log('Изображение вставлено из HTML-кода');
                        }
                    });
                }
            }

            setTimeout(function() {
                imagePasteArea.html('');
            }, 50);
        });

        removeImageButton.on('click', function(event) {
            event.preventDefault();
            imagePreview.hide();
            removeImageButton.hide();
            productImageInput.val('');
            imagePasteAreaBG.show();
            imagePasteArea.show();
        });

        imagePreviewContainer.on('dblclick', function(event) {
            productImageInput.click();
        });
    }

    $('.img_cell').each(function() {
        var img_cell = $(this);
        initializeCell(img_cell);
    });

});
