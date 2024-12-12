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
        // Получаем HTML из буфера обмена
        var pastedHTML = clipboardData.getData('text/html');

        // Парсим HTML
        var parser = new DOMParser();
        var doc = parser.parseFromString(pastedHTML, 'text/html');

        // Извлекаем строки из таблицы
        var rows = doc.querySelectorAll('table tr');
        console.log('rows', rows);

        // Проверяем количество форм и добавляем недостающие
        var existingForms = parseInt(totalForms.val());
        var formsToAdd = Math.max(0, rows.length - existingForms);

        for (var i = 0; i < formsToAdd; i++) {
            addEmptyForm();
            console.log('добавил форму:', i+1);
        }

        // Перезапоминаем новые строки для отображения ошибок
        initErrorHandling();

        // Собираем файлы и данные из буфера
        var { files, data } = processFiles(rows);

        // Заполняем строки формы
        rows.forEach((rows, rowIndex) => {
            populateForm(rowIndex, data[rowIndex], files[rowIndex]);
        });
    });

    function dataURLtoFile(dataurl, filename) {
        var arr = dataurl.split(','),
            mime = arr[0].match(/:(.*?);/)[1],
            bstr = atob(arr[1]),
            n = bstr.length,
            u8arr = new Uint8Array(n);
        while(n--){
            u8arr[n] = bstr.charCodeAt(n);
        }
        return new File([u8arr], filename, {type:mime});
    }

    function processFiles(rows) {
        var files = Array(rows.length).fill(null);
        var data = [];

        rows.forEach((row, rowIndex) => {
            var cells = row.querySelectorAll('td');
            var rowData = Array(cells.length).fill('');
            console.log('ряд', rowIndex);
            cells.forEach((cell, colIndex) => {

                var img = cell.querySelector('img');
                if (img) {
                    files[rowIndex] = dataURLtoFile(img.src, 'image.png');
                    console.log('Файл найден сразу, ряд', rowIndex);
                } else {
                    rowData[colIndex] = cell.textContent.trim();
                }
            });
            data.push(rowData);
        });
        return {files: files, data: data}
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
        var formRow = $(`.table-row-form tbody tr`).eq(rowIndex);
        console.log(formRow);
        console.log('заполняем:', rowIndex, rowData, "есть файл", file && true);

        rowData.forEach((value, colIndex) => {
            const fieldName = `form-${rowIndex}-${fieldNames[colIndex]}`;
            const field = formRow.find(`[name="${fieldName}"]`);
            console.log('PASTE field', `[name="${fieldName}"]`);
            console.log(value, field.length, field.attr('type'));

            if (field.length) {
                if (field.attr('type') === 'text' || field.is('textarea')) {
                    // Для текстовых полей
                    field.val(value);
                } else if (field.is('select')) {
                    // Для полей select
                    var optionToSelect = field.find('option').filter(function () {
                        return $(this).text().trim() === value.trim();
                    });
                    if (optionToSelect.length) {
                        console.log('PASTE select field', `[name="${fieldName}"]`);
                        field.val(optionToSelect.val()).change(); // Устанавливаем значение и вызываем событие изменения
                    } else {
                        console.warn(`Значение "${value}" не найдено в опциях select для поля ${fieldName}`);
                    }
                }
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
