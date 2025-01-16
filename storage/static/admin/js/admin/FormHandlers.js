django.jQuery(document).ready(function ($) {
    // Проверяем наличие formFields
    if (typeof formFields === 'undefined' || !Array.isArray(formFields)) {
        console.warn("formFields не определены!");
        return;
    } else {
        console.log("formFields:", formFields);
    }

    const $tableHeaders = $('.table-rows-form thead tr th');
    const $firstRow = $('.table-rows-form tbody tr').first();
    var relatedFieldIndices = []; // Массив индексов связанных полей
    var activeLink = null; // Хранение текущей активной ссылки

    // Вычисляем индексы связанных полей
    var idx = 0;
    $.each(formFields, function (index, field) {
        if (field.endsWith('_name') && formFields.includes(field.replace('_name', '_id'))) {
            relatedFieldIndices.push(idx); // Сохраняем индекс связанного поля
        }
        if (!field.endsWith('_id')) {
            idx++;
        }
    });

    if (!relatedFieldIndices.length) { return; }

    // Обрабатываем <th>, основываясь на вычисленных индексах
    $tableHeaders.each(function (thIndex) {
        if (relatedFieldIndices.includes(thIndex)) {
            const fieldName = formFields[thIndex]; // Имя текущего поля
            const $div = $firstRow.find('td').eq(thIndex).find('.related-widget-wrapper');
            const relatedModel = $div.data('model-ref');
            console.log('MODEL', relatedModel);

            // Создаем ссылку
            const $link = $('<a>')
                .attr('href', '#')
                .text($(this).text())
                .addClass('viewlinked') // Класс для стиля
                .data('relatedModel', relatedModel) // Сохраняем имя связанной модели
                .data('current', 'false'); // Указывает, активна ли таблица связанной модели

            $(this).empty().append($link); // Очистить содержимое <th> и вставить ссылку в заголовок

            // Добавляем обработчик для переключения таблицы
            $link.on('click', function (event) {
                event.preventDefault();

                var $relatedTable = $('#related-table'); // Таблица связанной модели

                // Если уже активен другой линк, деактивируем его
                if (activeLink && activeLink[0] !== $link[0]) {
                    activeLink.removeClass('hidelinked').addClass('viewlinked').data('current', 'false');
                    $relatedTable.hide().empty();
                }

                // Текущая ссылка: включение/выключение
                if ($link.data('current') === 'false') {
                    // Показать таблицу связанной модели
                    $.get(`/${appLabel}/${relatedModel}/related_table`, function (html) {
                        $relatedTable.html(html).show();
                        $link.removeClass('viewlinked').addClass('hidelinked').data('current', 'true');
                        activeLink = $link; // Обновляем текущую активную ссылку
                    });
                } else {
                    // Скрыть таблицу связанной модели
                    $relatedTable.hide().empty();
                    $link.removeClass('hidelinked').addClass('viewlinked').data('current', 'false');
                    activeLink = null; // Сбрасываем текущую активную ссылку
                }
            });
        }
    });
});


window.initErrorHandling = function () {
    console.log('Инициализация обработки ошибок и хелпер');

    django.jQuery(document).ready(function ($) {

        // Функция загрузки данных записи в форму
        function loadRecordData(link) {
            const obj_id = link.split('/')[0];
            console.log('ID', obj_id);
            $.get(link, function(data) {
                // Парсинг и установка значений полей формы
                const parser = new DOMParser();
                const doc = parser.parseFromString(data, 'text/html');
                const form = $('#input_form');
                const tr = form.find('tbody tr').first();

                $('#form_action').val('edit_'+obj_id);
                $('#submit_btn').val('Сохранить');

                // Обрабатываем input, select и textarea
                tr.find('input, select, textarea').each(function() {
                    const name = $(this).attr('name');
                    const field = $(`[name="${name}"]`);
                    const element = doc.querySelector(`[name="${name}"]`);
                    console.log('Найденный элемент:', element, element ? element.value : null);

                    if (element && !name.includes('product_image')) {
                        const value = element.value;
                        $(this).val(value);
                        $(this).trigger('change');
                        console.log("Имя/значение:", name, value);
                    }

                    // Обновление превью изображений
                    if (name.includes('product_image')) {
                        var imgContainer = $(element).closest('td').find('.image_preview_container');
                        var imagePreview = imgContainer.find('img')[0];
                        const imageUrl = imagePreview.src;
                        console.log('URL элемент:', imageUrl);

                        if (imageUrl) {
                            imgContainer = $(this).closest('td').find('.image_preview_container');
                            imagePreview = imgContainer.find('img')[0];
                            imagePreview.src = imageUrl;
                            const removeButton = $(this).closest('td').find('.remove_image_button');
                            const bg = $(this).closest('td').find('.image_paste_area_bg');
                            $(imagePreview).show();
                            $(removeButton).show();
                            $(bg).hide();

                            const fileName = imageUrl.substring(imageUrl.lastIndexOf('/') + 1);

                            // Преобразуем URL изображения в файл и внедряем его в инпут
                            fetch(imageUrl)
                                .then(response => response.blob())
                                .then(blob => {
                                    const file = new File([blob], fileName, { type: blob.type });
                                    const fileInput = $(this).closest('td').find('input[type="file"]')[0];

                                    // Создаем DataTransfer для обновления инпута
                                    const dataTransfer = new DataTransfer();
                                    dataTransfer.items.add(file);
                                    fileInput.files = dataTransfer.files;
                                })
                                .catch(error => console.error('Ошибка при загрузке изображения:', error));

                        }

                    }
                });
                let idField = form.find('input[name="id"]');
                if (!idField.length) {
                    idField = $('<input>').attr({
                        type: 'hidden',
                        name: 'id',
                        value: obj_id
                    });
                    form.append(idField);
                } else {
                    idField.val(obj_id);
                }

                console.log('тип формы', $('#form_action').val());

                // Обновление превью изображений и других элементов
                initializeAutoCompleteFields();
                $(this).closest('td').each(function() {
                    initializeCell($(this));
                });
            });
        }

        // Передача строки для редактирования в форме
        const appTable = $('#result_list');
        if (appTable.length) {
            var headers = appTable.find('th');
            headers.each(function() {
                const th = $(this);
                const link = th.find('a');
                const url = link.attr('href');

                link.attr('href', '#');
                if (link.length) {
                    th.css('cursor', 'pointer');
                    th.addClass('custom_list_apps');
                    th.on('click', function() {
                        console.log('URL:', url);
                        loadRecordData(url);
                    });
                }
            });
        }

        const $password_sha = $('#id_password');
        if ($password_sha.length) {
            const $firstP = $password_sha.find('p').first();
            if ($firstP.length) {
                $firstP.css('display', 'none');
            }
        }

        const $appTableNav = $('#nav-sidebar');
        if ($appTableNav.length) {
            const $headers = $appTableNav.find('th');
            $headers.each(function() { const $th = $(this);
                const $link = $th.find('a');
                if ($link.length) { $th.on('click', function() { window.location.href = $link.attr('href'); }); }
            });
        }

        // Функция для переключения состояния поля Причина возврата поставщику
        function toggleSupplierReason(row) {
            var processTypeSelect = $(row).find('select[name$="-process_type"]');
            var returnToSupplierReasonSelect = $(row).find('select[name$="-return_to_supplier_reason"]');
            var selectedValue = processTypeSelect.val();

            if (selectedValue === 'sup_return') {
                returnToSupplierReasonSelect.prop('disabled', false);
                returnToSupplierReasonSelect.css('background', '');

            } else {
                returnToSupplierReasonSelect.prop('disabled', true);
                returnToSupplierReasonSelect.css('background', '#eee');

            }
        }
        // Функция для переключения состояния поля Адрес доставки
        function toggleDeliveryAddress(row) {
            var deliveryLocationSelect = $(row).find('select[name$="-delivery_location"]');
            var deliveryAddressField = $(row).find('input[name$="-delivery_address"]');
            var selectedValue = deliveryLocationSelect.val();
            console.log('selectedValue', selectedValue);

            if (['Монтаж', 'Подрядчик', 'Заказчик'].includes(selectedValue)) {
                deliveryAddressField.prop('disabled', false);
                deliveryAddressField.css('background', ''); // Возвращает стандартный цвет фона
            } else {
                deliveryAddressField.prop('disabled', true);
                deliveryAddressField.css('background', '#eee'); // Меняет цвет фона на серый
            }
        }

        function applyToggleToAllRows() {
            var rows = $('.table-rows-form tbody tr');
            rows.each(function() {
                toggleSupplierReason(this);
                $(this).find('select[name$="-process_type"]').change(function() {
                    toggleSupplierReason(this.closest('tr'));
                });
                toggleDeliveryAddress(this);
                $(this).find('select[name$="-delivery_location"]').change(function() {
                    toggleDeliveryAddress(this.closest('tr'));
                });
            });
             console.log('Toggle applied');
        }

        applyToggleToAllRows();
        // Применение функции к новым строкам, добавленным в formset
        $(document).on('formset:added', function(event, $row, formsetName) {
            toggleSupplierReason($row);
            $row.find('select[name$="-process_type"]').change(function() {
                toggleSupplierReason(this.closest('tr'));
            });
            toggleDeliveryAddress($row);
            $row.find('select[name$="-delivery_location"]').change(function() {
                toggleDeliveryAddress(this.closest('tr'));
            });
        });

        // Обработка ошибок, присутствующих при загрузке страницы
        $('.error-field').each(function () {
            var errorField = $(this);

            var errorList = errorField.find('ul.errorlist li');
            var errorMessage = errorList.length ? errorList.text() : '';

            var cell = errorField.closest('td');
            var cellIndex = cell.index();

            var table = cell.closest('table');
            var caption = table.find('thead tr th').eq(cellIndex).text().trim();

            if (errorMessage) {
                console.log('Обнаружена ошибка:', caption, errorMessage);
                cell.css('border-bottom', '3px solid #ba2121');
                var text = $('#errors_viewer').text();
                if (!(text.includes(caption))) {
                    text += '<br><b>' + caption + ':</b> ' + errorMessage;
                    $('#errors_viewer').html(text);
                }
            }
        });

        $('input[type="file"]').each(function () {
            var fileInput = $(this);

            // есть ли загруженный файл
            if (fileInput[0].files.length > 0) {
                var file = fileInput[0].files[0];
                var reader = new FileReader();

                // Читаем файл и обновляем соответствующий <img>
                reader.onload = function (e) {
                    var fieldName = fileInput.attr('name'); // Имя поля (например, form-1-product_image)
                    var cell = fileInput.closest('td'); // Ячейка, содержащая input
                    var imagePreview = cell.find('.image_preview'); // Ищем <img> в этой ячейке

                    if (imagePreview.length) {
                        imagePreview.attr('src', e.target.result).show(); // Устанавливаем изображение
                        cell.find('.remove_image_button').show(); // Показываем кнопку удаления, если есть
                        console.log('Превью установлено для:', fieldName);
                    } else {
                        console.warn('Превью не найдено для:', fieldName);
                    }
                };

                reader.readAsDataURL(file);
            }
        });

        // Убираем ошибки при фокусе
        $('td').on('focusin', function () {
            var cell = $(this);
            var errorField = cell.find('.error-field');
            $('#errors_viewer').html('');
            errorField.html(''); // Очистка ошибок
            cell.css('border-bottom', ''); // Сброс подсветки ячейки
        });
    });
};

window.initFilePreviews = function () {
    console.log('Инициализация превью изображений');
    django.jQuery(document).ready(function ($) {
        // Проходим по данным из initialFileData
        Object.keys(initialFileData).forEach(function (fieldName) {
            var fileUrl = initialFileData[fieldName]; // URL изображения
            var inputField = $('input[name="' + fieldName + '"]'); // Находим input по имени
            var cell = inputField.closest('td'); // Ячейка с input
            var imagePreview = cell.find('.image_preview'); // Находим <img> для превью

            if (imagePreview.length) {
                imagePreview.attr('src', fileUrl).show(); // Устанавливаем изображение
                cell.find('.remove_image_button').show(); // Показываем кнопку удаления, если есть
                console.log('Превью установлено для:', fieldName);
            } else {
                console.warn('Превью не найдено для:', fieldName);
            }
        });
    });
};

// Подключение скрипта после загрузки страницы
document.addEventListener('DOMContentLoaded', function () {
    initErrorHandling();
});

// Очистка форм
function resetForm() {
    // Установить TOTAL_FORMS в 1
    document.getElementById('id_form-TOTAL_FORMS').value = '1';
    document.getElementById('id_form-INITIAL_FORMS').value = '0';

    // Найти tbody и все строки в нем
    const tbody = document.querySelector('table.table-rows-form tbody');
    const rows = tbody.querySelectorAll('tr');

    // Удалить все строки, кроме первой и строки с ID #empty_form
    rows.forEach((row, index) => {
        if (index > 0 && row.id !== 'empty_form') {
            tbody.removeChild(row);
        }
    });

    // Очистить все input и select в первой строке
    const firstRowInputs = rows[0].querySelectorAll('input, select');
    firstRowInputs.forEach(input => {
        console.log(input.tagName, input.type, input.value, '-> сброс!' )
        if (input.tagName === 'INPUT') {
            if(!['submit', 'reset'].includes(input.type)){
                 input.value = '';
                 input.dispatchEvent(new Event('change'));
            }
        } else if (input.tagName === 'SELECT') {
            input.selectedIndex = 0; // Выбрать первый пункт
            input.dispatchEvent(new Event('change'));
        }

    });

    // Убрать ошибки валидации, если они есть
    const errorFields = document.querySelectorAll('.error-field');
    errorFields.forEach(field => {
        field.textContent = '';
    });

    // Удалить превью изображений, если есть и восстановить поля вставки
    const imagePreviews = document.querySelectorAll('.image_preview');
    imagePreviews.forEach(img => {
        img.src = '#';
        img.style.display = 'none';
    });
    const removeButtons = document.querySelectorAll('.remove_image_button');
    removeButtons.forEach(button => {
        button.style.display = 'none';
    });
    var imagePasteArea = document.querySelectorAll('.image_paste_area_bg');
    imagePasteArea.forEach(button => {
        button.style.display = 'block';
    });
    imagePasteArea = document.querySelectorAll('.image_paste_area');
    imagePasteArea.forEach(button => {
        button.style.display = 'block';
    });
    document.getElementById('form_action').value = 'add';
}