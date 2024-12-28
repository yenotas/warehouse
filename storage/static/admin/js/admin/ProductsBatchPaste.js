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


    $('#id_form-0-' + formFields[0]).on('paste', async function (event) {
        event.preventDefault();

        var clipboardData = (event.originalEvent || event).clipboardData || window.clipboardData;

        var pastedText = clipboardData.getData('Text');
        if (!pastedText.includes("\t") && !pastedText.includes("\n")) {
            console.log('Text', pastedText);
            $('#id_form-0-' + formFields[0]).val(pastedText);
            return;
        }
        var rows = pastedText.split(/\r?\n/);
        var dataRows = rows.map(row => row.trim().split('\t'));

        // var maxElements = Math.max(...dataRows.map(row => row.length));
        // Найти строки без текста и запомнить их индексы
        var emptyRowsIndex = dataRows.map((row, index) => row.every(cell => cell === '') ? index : -1).filter(index => index !== -1);

        // Удаление пустых строк
        var textTable = dataRows.filter((row, index) => !emptyRowsIndex.includes(index));
        console.log('Матрица:', textTable);

        // Парсим HTML
        var pastedHTML = clipboardData.getData('text/html');
        var parser = new DOMParser();
        var html = parser.parseFromString(pastedHTML, 'text/html');

        // Извлекаем строки из таблицы
        var htmlTable = html.querySelectorAll('table tr');
        console.log('htmlTable:', Array.from(htmlTable));

        // Проверяем количество форм и добавляем недостающие
        var existingForms = parseInt(totalForms.val());
        var formsToAdd = Math.max(0, textTable.length - existingForms);

        for (var i = 0; i < formsToAdd; i++) {
            addEmptyForm();
            console.log('добавил форму:', i+1);
        }

        // Перезапоминаем новые строки для отображения ошибок
        initErrorHandling();

        // Собираем файлы
        var files = await processFiles(Array.from(htmlTable), emptyRowsIndex);
        // Заполняем строки формы
        await Promise.all(textTable.map(async (row, i) => { // Ожидаем завершения всех промисов
            await populateForm(i, row, files[i]); // Ожидаем завершения populateForm
        }));
    });

    async function fetchFile(url, fileName = 'downloaded_file') {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Ошибка загрузки файла: ${response.statusText}`);
            }
            const blob = await response.blob();
            return new File([blob], fileName, { type: blob.type });
        } catch (error) {
            console.error('Ошибка загрузки:', error);
            return null;
        }
    }

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

    async function processFiles(rows, emptyRowsIndex) {
        var i = 0;
        var result = await Promise.all(

            rows
                .filter((_, rowIndex) => !emptyRowsIndex.includes(rowIndex)) // Убираем ненужные индексы
                .map(async (row) => {
                    const img = row.querySelector('img');
                    if (img) {
                        const filename = 'image'+i+'.png';
                        i++;
                        const src = img.getAttribute('src');
                        return src.startsWith('data:image/')
                            ? dataURLtoFile(src, filename)
                            : await fetchFile(src, filename);
                    }
                    return null;
                })
        );
        return result;
    }

    function addEmptyForm() {
        var formIndex = parseInt(totalForms.val());
        var emptyFormHtml = $('#empty_form').html().replace(/__prefix__/g, formIndex);

        $('#empty_form').before('<tr>' + emptyFormHtml + '</tr>');

        totalForms.val(formIndex + 1);
        var newRow = $('#empty_form').prev(); // Последняя добавленная строка

        // Обновляем имя и id у всех input в новой строке
        newRow.find('input, select, textarea').each(function() {
            var name = $(this).attr('name');
            var id = $(this).attr('id');
            if (name) {
                var newName = name.replace('__prefix__', formIndex);
                $(this).attr('name', newName);
            }
            if (id) {
                var newId = id.replace('__prefix__', formIndex);
                $(this).attr('id', newId);
            }
        });

        newRow.find('.img_cell').each(function () {
            initializeCell($(this));
        });
    }


    async function populateForm(rowIndex, rowData, file) {
        var formRow = $(`.table-rows-form tbody tr`).eq(rowIndex);

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
            console.log('PASTE IMAGE', file.name, rowIndex);
            await insertImageToCell(formRow, file);
        }
    }

    async function insertImageToCell(formRow, file) {
        var imgCell = formRow.find('.img_cell');
        if (imgCell.length) {
            var imageCell = new ImageCell(imgCell);
            await imageCell.insertImage(file);
        }
    }
});
