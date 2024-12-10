django.jQuery(document).ready(function($) {
    var totalForms = $('#id_form-TOTAL_FORMS');

    $('#id_form-0-' + formFields[0]).on('paste', function(event) {
        event.preventDefault();

        var clipboardData = (event.originalEvent || event).clipboardData || window.clipboardData;
        var items = clipboardData.items;

        // Определяем текстовые и файловые данные
        var pastedText = clipboardData.getData('Text');
        var files = Array.from(items).filter(item => item.kind === 'file');
        console.log('файлов найдено', files.length);

        processPastedDataAndFiles(pastedText, files);
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
                    console.log('имя ячейки с img', name);
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
        var productImageInput = imgCell.find('.product_image');
        var imagePreview = imgCell.find('.image_preview');
        var imagePasteAreaBG = imgCell.find('.image_paste_area_bg');
        var removeImageButton = imgCell.find('.remove_image_button');

        resizeImage(file, 50, 50, function(resizedFile, dataURL) {
            var container = new DataTransfer();
            container.items.add(resizedFile);
            productImageInput[0].files = container.files;

            imagePreview.attr('src', dataURL);
            imagePasteAreaBG.hide();
            imagePreview.show();
            removeImageButton.show();
        });
    }

    function resizeImage(file, maxWidth, maxHeight, callback) {
        var reader = new FileReader();
        reader.onload = function(event) {
            var img = new Image();
            img.onload = function() {
                var canvas = document.createElement('canvas');
                canvas.width = maxWidth;
                canvas.height = maxHeight;
                var ctx = canvas.getContext('2d');

                ctx.clearRect(0, 0, maxWidth, maxHeight);
                ctx.drawImage(img, 0, 0, maxWidth, maxHeight);

                canvas.toBlob(function(blob) {
                    var resizedFile = new File([blob], file.name, {
                        type: file.type,
                        lastModified: Date.now()
                    });
                    callback(resizedFile, canvas.toDataURL(file.type));
                }, file.type);
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }
});
