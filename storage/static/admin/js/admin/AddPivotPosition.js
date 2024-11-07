$(document).ready(function() {
    // Инициализация DataTables, если используется
    $('#pivot-table').DataTable({
        paging: false, // Отключаем пагинацию DataTables, используем серверную пагинацию Django
        searching: true,
        ordering: true,
        // Другие настройки
    });

    // Обработчик для редактирования ячеек
    $('.editable').on('blur', function() {
        var td = $(this);
        var newValue = td.text();
        var field = td.data('field');
        var id = td.closest('tr').data('id');

        // Отправка AJAX-запроса для обновления данных
        $.ajax({
            url: '{% url "pivot_table_update" %}',
            type: 'POST',
            data: {
                'id': id,
                'field': field,
                'value': newValue,
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            success: function(response) {
                // Обработка успешного ответа
                console.log('Данные успешно обновлены');
            },
            error: function(xhr, status, error) {
                // Обработка ошибок
                console.error('Ошибка обновления данных:', error);
            }
        });
    });
});