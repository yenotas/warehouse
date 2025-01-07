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

    // Обработчик события вставки на таблицу
    $('.table-rows-form').on('paste', 'td', async function (event) {

        var clipboardData = (event.originalEvent || event).clipboardData || window.clipboardData;
        var pastedText = clipboardData.getData('Text');

        // Обработка текстов с переносом на другую строку, заключенных в кавычки
        var rows = [];
        var tempRow = "";
        var inQuotes = false;
        pastedText.split("").forEach(char => {
            if (char === '"') {
                inQuotes = !inQuotes;
                return;
            }
            if (char === "\n" && !inQuotes) {
                rows.push(tempRow.trim());
                tempRow = "";
            } else if (!(char === "\n" && inQuotes)) {
                tempRow += char;
            }
        });
        if (tempRow) {
            rows.push(tempRow.trim());
        }

        var dataRows = rows.map(row => row.trim().split('\t'));

        if ((rows.length == 1 && dataRows.length == 1) || (!pastedText.includes("\t") && !pastedText.includes("\n"))) {
            console.log('Просто вставка текста в ячейку', pastedText);
            return;
        }
        event.preventDefault();
        $('#form_action').val('add');
        var emptyRowsIndex = dataRows.map((row, index) => row.every(cell => cell === '') ? index : -1).filter(index => index !== -1);
        var textTable = dataRows.filter((row, index) => !emptyRowsIndex.includes(index));
        console.log('Матрица:', textTable);

        var pastedHTML = clipboardData.getData('text/html');
        var parser = new DOMParser();
        var html = parser.parseFromString(pastedHTML, 'text/html');
        var htmlTable = html.querySelectorAll('table tr');
        console.log('htmlTable:', Array.from(htmlTable));

        var existingForms = parseInt(totalForms.val());
        var formsToAdd = Math.max(0, textTable.length - existingForms);

        for (var i = 0; i < formsToAdd; i++) {
            addEmptyForm();
            console.log('добавил форму:', i+1);
        }

        initErrorHandling();

        var files = await processFiles(Array.from(htmlTable), emptyRowsIndex);

        var startRowIndex = $(this).closest('tr').index();
        var startColIndex = $(this).index();

        // Пропускаем первые ячейки с числом, если целевая ячейка текстовая
        if (isNumber(textTable[0][0]) && isTextField($(this).find('input, textarea'))) {
            textTable = textTable.map(row => row.slice(1));
        }

        // Найти данные справа от начальной ячейки вставки
        let existingRowData = [];
        let existingImage = null;
        $(this).closest('tr').find('td').each(function(index) {
            const input = $(this).find('input, textarea, select');
            if (input.length && index >= startColIndex) {
                existingRowData.push(input.val() || '');
            }
            const imageInput = $(this).find('input.product_image');
            if (imageInput.length && imageInput[0].files.length > 0 && !existingImage) {
                existingImage = imageInput[0].files[0];
                console.log(`Найдено изображение: ${existingImage.name}`);
            }
        });

        // Если изображение найдено, заменяем весь массив files на него
        if (existingImage) {
            files = files.map(() => existingImage);
        }

        console.log('Существующие данные:', String(existingRowData));

        // Заменяем в каждой строке textTable часть данных существующими данными справа
        textTable = textTable.map(row => {
          // Для каждой строки `row` в textTable копируем данные из шаблона existingRowData
          return row.map((cell, colIndex) => {
            // Если в шаблоне есть данные для этого столбца, и они не пустые, используем их
            return existingRowData[colIndex] && existingRowData[colIndex] !== ""
              ? existingRowData[colIndex]
              : cell; // Иначе оставляем существующие данные из textTable
          }).concat(existingRowData.slice(row.length)); // Добавляем недостающие данные из шаблона
        });

        console.log('textTable данные:', String(textTable));

        // Заполняем формы
        await Promise.all(textTable.map(async (row, i) => {
            await populateForm(startRowIndex + i, row, startColIndex, files[i]);
        }));
        // Обновляем автозаполнение
        initializeAutoCompleteFields();
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
                .filter((_, rowIndex) => !emptyRowsIndex.includes(rowIndex))
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

    async function populateForm(rowIndex, rowData, startColIndex, file) {
        var formRow = $(`.table-rows-form tbody tr`).eq(rowIndex);
        var existingData = {};

        // Сохраняем существующие данные справа от вставки
        formRow.find('input, textarea, select').each((index, element) => {
            var name = $(element).attr('name');
            var nameMatch = name.match(/form-\d+-\d+/);
            if (nameMatch) {
                var colIndex = parseInt(nameMatch[0].split('-')[2]);
                if (colIndex >= startColIndex) {
                    existingData[colIndex] = $(element).val();
                }
            }
        });

        rowData.forEach((value, colIndex) => {
            const fieldName = `form-${rowIndex}-${fieldNames[startColIndex + colIndex]}`;
            const field = formRow.find(`[name="${fieldName}"]`);
            console.log('PASTE field', `[name="${fieldName}"]`);
            console.log(value, field.length, field.attr('type'));

            if (field.length) {
                if (field.attr('type') === 'text' || field.is('textarea')) {
                    // Обработка частного случая вставки для таблицы проектов
                    if (fieldNames[startColIndex + colIndex] === 'detail_code'){
                        value = `АРХ${parseInt(value.replace('АРХ', '')) + 1 + rowIndex}`;
                    }
                    field.val(value);
                } else if (field.is('select')) {
                    var optionToSelect = field.find('option').filter(function () {
                        return $(this).text().trim() === value.trim();
                    });
                    if (optionToSelect.length) {
                        console.log('PASTE select field', `[name="${fieldName}"]`);
                        field.val(optionToSelect.val()).change();
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

    function isNumber(value) {
        return !isNaN(value) && !isNaN(parseFloat(value));
    }

    function isTextField(element) {
        return element.is('input[type="text"]') || element.is('textarea');
    }
});