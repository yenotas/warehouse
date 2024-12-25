window.initErrorHandling = function () {
    console.log('Инициализация обработки ошибок');
    django.jQuery(document).ready(function ($) {
        // Обработка ошибок, присутствующих при загрузке страницы
        $('.error-field').each(function () {
            var errorField = $(this);

            var errorList = errorField.find('ul.errorlist li');
            var errorMessage = errorList.length ? errorList.text() : '';

            // Получаем индекс ячейки в строке таблицы
            var cell = errorField.closest('td');
            var cellIndex = cell.index(); // Индекс ячейки в строке

            // Получаем соответствующий заголовок из <th>
            var table = cell.closest('table');
            var caption = table.find('thead tr th').eq(cellIndex).text().trim();

            // Если ошибка найдена, отображаем её
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

            // Проверяем, есть ли загруженный файл
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

function resetForm() {
    // Установить TOTAL_FORMS в 1
    document.getElementById('id_form-TOTAL_FORMS').value = '1';
    document.getElementById('id_form-INITIAL_FORMS').value = '0';

    // Найти tbody и все строки в нем
    const tbody = document.querySelector('table.table-row-form tbody');
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