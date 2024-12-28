django.jQuery(document).ready(function ($) {
    var totalForms = $('#id_form-TOTAL_FORMS');
    var fieldNames = [];
    $('tr:first-child').find('[name^="form-0-"]').each(function(index) {
        var name = $(this).attr('name');
        var type = $(this).attr('type');
        if (type !== 'hidden') {
            fieldNames.push(name.replace(/^form-0-/, ''));
        }
    });
    console.log('fieldNames:', fieldNames);


    $('#id_form-0-' + formFields[0]).on('paste', function (event) {
        event.preventDefault();

        var clipboardData = (event.originalEvent || event).clipboardData || window.clipboardData;
        var pastedText = clipboardData.getData('Text');
        console.log('pastedText:', pastedText);

        // 1. Разбиваем текст на строки и ячейки
        var rows = pastedText.split(/\r?\n/).filter(Boolean); // Убираем пустые строки
        var dataRows = rows.map(row => row.split('\t'));

        // 2. Проверяем количество форм и добавляем недостающие
        var existingForms = parseInt(totalForms.val());
        var formsToAdd = Math.max(0, dataRows.length - existingForms);

        for (var i = 0; i < formsToAdd; i++) {
            addEmptyForm();
            console.log('добавил форму:', i+1);
        }

        initErrorHandling(); // Перезапоминаем новые строки для отображения ошибок


        // 3. Собираем файлы из буфера
        var items = clipboardData.items;
        processFiles(dataRows, items).then((files) => {

            console.log('Все файлы обработаны', files);

            // 4. Заполняем строки формы
            dataRows.forEach((rowData, rowIndex) => {
                populateForm(rowIndex, rowData, files[rowIndex]);
            });
        });
    });

    function processFiles(dataRows, items) {
        var files = Array(dataRows.length).fill(null);

        // Создаем массив промисов для всех строк
        var promises = dataRows.map((_, i) => {
            return new Promise((resolve) => {
                var item = items[i];
                console.log('ряд', i);
                if (item && item.kind === 'file') {
                    files[i] = item.getAsFile();
                    console.log('Файл найден сразу, ряд', i);
                    resolve(); // Уведомляем, что обработка завершена
                } else if (item) {
                    getImageFromHTML(item, function(file) {
                        if (file) {
                            files[i] = file;
                            console.log('Файл обработан через HTML, ряд', i);
                        }
                        resolve(); // Уведомляем, что обработка завершена
                    });
                } else {
                    resolve(); // Если элемента нет, ничего не делаем
                }
            });
        });

        // Ждем завершения всех промисов
        return Promise.all(promises).then(() => files);
    }

    function addEmptyForm() {
        var formIndex = parseInt(totalForms.val());
        var emptyFormHtml = $('#empty_form').html().replace(/__prefix__/g, formIndex);

        $('#empty_form').before('<tr>' + emptyFormHtml + '</tr>');

        totalForms.val(formIndex + 1);
        var newRow = $('#empty_form').prev(); // Последняя добавленная строка
        newRow.find('.img_cell').each(function () {
            initializeCell($(this));
        });
    }


    function populateForm(rowIndex, rowData, file) {
        var formRow = $(`.table-rows-form tbody tr`).eq(rowIndex);
        console.log(formRow);
        console.log('заполняем:', rowIndex, rowData, "есть файл", file && true);
        rowData.forEach((value, colIndex) => {
            const fieldName = `form-${rowIndex}-${fieldNames[colIndex]}`;
            const field = formRow.find(`[name="${fieldName}"]`);

            if (field.length && (field.attr('type') === 'text' || field.is('textarea'))) {
                console.log('PASTE field', `[name="${fieldName}"]`);
                console.log(value, field.length, field.attr('type'));
                field.val(value);
            }
        });

        if (file) {
            insertImageToCell(formRow, file);
        }
    }

    function insertImageToCell(formRow, file) {
        var imgCell = formRow.find('.img_cell');

        if (imgCell.length) {
            var imageCell = new ImageCell(imgCell);
            imageCell.insertImage(file);
        }
    }
});
