window.initErrorHandling = function () {
    console.log('Инициализация обработки ошибок и хелперов');

    django.jQuery(document).ready(function ($) {

        // Функция загрузки данных записи в форму
        function loadRecordData(recordId) {
            $.get(`/admin/storage/modelname/${recordId}/change/`, function(data) {
                // Парсинг и установка значений полей формы
                const parser = new DOMParser();
                const doc = parser.parseFromString(data, 'text/html');
                const form = doc.querySelector('form');

                $(form).find('input, select, textarea').each(function() {
                    const field = $(`[name="${this.name}"]`);
                    if (field.length) {
                        field.val($(this).val());
                    }
                });

                // Обновление превью изображений и других элементов
                initializeAutoCompleteFields();
                $('.img_cell').each(function() {
                    initializeCell($(this));
                });
            });
        }

        // Обработчик клика по строке таблицы
        $('.results tr').on('click', function() {
            const recordId = $(this).data('id');
            if (recordId) {
                loadRecordData(recordId);
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const activeElement = document.activeElement;
                if (activeElement.tagName === 'INPUT' && activeElement.type === 'text') {
                    activeElement.value = '';
                    if ($(activeElement).hasClass('auto_complete')) {
                        $(activeElement).blur();
                        setTimeout(function() { activeElement.focus(); }, 10)
                    }
                }
            }
            // if (e.ctrlKey && e.key === 'Delete') {
            //    e.preventDefault();
            //    removeFocusedRow();
            // }
        });

        const $password_sha = $('#id_password');
        if ($password_sha.length) {
            const $firstP = $password_sha.find('p').first();
            if ($firstP.length) {
                $firstP.css('display', 'none');
            }
        }

        // Открытие строки для редактирования в форме
        const $appTable = $('#result_list');
        if ($appTable.length) {
          const $headers = $appTable.find('th');
          $headers.each(function() { const $th = $(this);
              const $link = $th.find('a');
              if ($link.length) { $th.css('cursor', 'pointer');
                  $th.addClass('custom_list_apps');
                  $th.on('click', function() { window.location.href = $link.attr('href'); });
              }
          });
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

            if (['Монтаж', 'Подрядчик', 'Заказчик'].includes(selectedValue)) {
                deliveryAddressField.prop('disabled', false);
                deliveryAddressField.css('background', ''); // Возвращает стандартный цвет фона
            } else {
                deliveryAddressField.prop('disabled', true);
                deliveryAddressField.css('background', '#eee'); // Меняет цвет фона на серый
            }
        }

        function applyToggleToAllRows() {
            var rows = $('.results tbody tr');
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


        // Функция для удаления строки формы из formset
        function removeFocusedRow() {
            var focusedElement = $(':focus');
            var formRow = focusedElement.closest('tr'); // Замените 'tr' на класс строки формы, если у вас другой

            if (formRow.length) {
                // Установим DELETE поле в True
                formRow.find('input[type="checkbox"][name$="-DELETE"]').prop('checked', true);

                // Добавим класс скрытия для визуального удаления строки
                formRow.addClass('hidden'); // Убедитесь, что CSS класс 'hidden' скрывает элемент

                console.log('Row marked for deletion.');

                // Установить фокус на следующей строке, если существует
                var nextRow = formRow.next('tr');
                if (nextRow.length) {
                    nextRow.find('input, select').first().focus();
                } else {
                    // Если следующей строки нет, установить фокус на предыдущей строке
                    var prevRow = formRow.prev('tr');
                    if (prevRow.length) {
                        prevRow.find('input, select').first().focus();
                    }
                }
            } else {
                console.log('No focused form row found.');
            }
        }
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

    // Удалить все строки, кроме первой
    rows.forEach((row, index) => {
        if (index > 0) {
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

    // Удалить превью изображений, если есть
    const imagePreviews = document.querySelectorAll('.image_preview');
    imagePreviews.forEach(img => {
        img.src = '#';
        img.style.display = 'none';
    });

    const removeButtons = document.querySelectorAll('.remove_image_button');
    removeButtons.forEach(button => {
        button.style.display = 'none';
    });
}