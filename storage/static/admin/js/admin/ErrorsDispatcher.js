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

// Подключение скрипта после загрузки страницы
document.addEventListener('DOMContentLoaded', function () {
    initErrorHandling();
});
