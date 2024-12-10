django.jQuery(document).ready(function($) {
    var totalForms = $('#id_form-TOTAL_FORMS');

    // Функция масштабирования изображения (из MultiRowsImgPaste.js)
    function resizeImage(file, maxHeight, callback) {
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

    // Обработка вставки HTML-кода с изображением в формате base64 (из MultiRowsImgPaste.js)
    function getImageFromHTML(item, callback) {
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

    $('#id_form-0-' + formFields[0]).on('paste', function(event) {
        event.preventDefault();

        var clipboardData = (event.originalEvent || event).clipboardData || window.clipboardData;
        var items = clipboardData.items;

        // Определяем текстовые и файловые данные
        var pastedText = clipboardData.getData('Text');
        var files = [];

        // Извлекаем файлы и изображения из Base64
        for (var i = 0; i < items.length; i++) {
            var item = items[i];
            if (item.kind === 'file') {
                files.push(item);
            } else if (item.kind === 'string') {
                getImageFromHTML(item, function(file) {
                    if (file) {
                        // Адаптируем под формат files
                        files.push({ getAsFile: function() { return file; } });
                    }
                });
            }
        }

        // Небольшая задержка, чтобы дождаться обработки Base64
        setTimeout(function() {
            processPastedDataAndFiles(pastedText, files);
        }, 50);
    });

    function processPastedDataAndFiles(pastedText, files) {
        // Получаем имена полей из первой строки формы
        var fieldNames = [];
        var imageFieldIndex = -1; // Индекс для поля с "_image"
        $('tr:first-child').find('[name^="form-0-"]').each(function(index) {
            var name = $(this).attr('name');
            var type = $(this).attr('type');
            if (type !== 'hidden') {
                fieldNames.push(name.replace(/^form-0-/, ''));
                if (name.endsWith('_image')) {
                    imageFieldIndex = index;
                }
            }
        });

        if (!fieldNames.length) {
            console.error('Не удалось найти имена полей.');
            return;
        }

        // Обработка текстовых данных
        var rows = pastedText.trim().split(/\r?\n/);
        var dataRows = rows.map(row => row.split('\t'));

        // Добавляем недостающие формы
        var existingForms = parseInt(totalForms.val());
        var formsToAdd = Math.max(0, dataRows.length - existingForms);
        for (var i = 0; i < formsToAdd; i++) {
            addEmptyForm();
        }

        // Заполняем формы
        dataRows.forEach((rowData, rowIndex) => {
            populateForm(rowIndex, rowData, fieldNames, imageFieldIndex, files);
        });
    }

    function addEmptyForm() {
        var formIndex = parseInt(totalForms.val());
        var emptyFormHtml = $('#empty_form').html().replace(/__prefix__/g, formIndex);
        $('.table-row-form tbody').append('<tr>' + emptyFormHtml + '</tr>');

        totalForms.val(formIndex + 1);

        var newRow = $('.table-row-form tbody tr').last();
        newRow.find('.img_cell').each(function() {
            initializeImgCell($(this));
        });
    }

    function populateForm(rowIndex, rowData, fieldNames, imageFieldIndex, files) {
        rowData.forEach((value, colIndex) => {
            if (colIndex >= fieldNames.length) return;

            var fieldName = fieldNames[colIndex];
            var field = $(`[name="form-${rowIndex}-${fieldName}"]`);

            // Пропускаем, если поле не найдено
            if (!field.length) return;

            // Заполняем текстовые поля
            if (colIndex !== imageFieldIndex && (field.attr('type') === 'text' || field.is('textarea'))) {
                field.val(value);
            }
        });

        // Если есть файл изображения для текущей строки, вставляем его
        if (imageFieldIndex !== -1 && files[rowIndex]) {
            var file = files[rowIndex].getAsFile();
            insertImageToCell(rowIndex, imageFieldIndex, file);
        }
    }

    function insertImageToCell(rowIndex, imageFieldIndex, file) {
        var imgCell = $(`tr:nth-child(${rowIndex + 1})`).find('.img_cell');
        var productImageInput = imgCell.find('.image_paste_area');
        var imagePreview = imgCell.find('.image_preview');
        var imagePasteAreaBG = imgCell.find('.image_paste_area_bg');
        var removeImageButton = imgCell.find('.remove_image_button');

        resizeImage(file, 50, function(resizedFile, dataURL) {
            var container = new DataTransfer();
            container.items.add(resizedFile);
            productImageInput[0].files = container.files;

            imagePreview.attr('src', dataURL);
            imagePasteAreaBG.hide();
            imagePreview.show();
            removeImageButton.show();
        });
    }

    // ... (остальной код) ...
});