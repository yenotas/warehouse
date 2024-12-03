django.jQuery(document).ready(function($) {
    $('#result_list .field-[class^="field-"]').click(function() {  // Обрабатываем клик только по редактируемым ячейкам
        var cell = $(this);
        var field = cell.data('field');
        var pk = cell.data('pk');
        var relatedModel = cell.data('related-model');
        var changeUrl = cell.data('change-url');
        var originalValue = cell.text();

        // Проверяем, что ячейка еще не в режиме редактирования
        if (cell.find('input').length === 0) {

            // Заменяем содержимое ячейки на поле ввода или форму
            if (relatedModel) {
                // Открываем форму редактирования связанной модели
                var url = changeUrl + '?_popup=1';
                window.open(url, 'Edit', 'width=800,height=600');
            } else {
                var input = $('<input type="text" value="' + originalValue + '">');
                cell.html(input);
                input.focus();

                // Обработчик потери фокуса, нажатия Enter или Esc
                input.on('blur keypress keydown', function(e) {
                    if (e.type === 'blur' || (e.type === 'keypress' && e.which === 13) || (e.type === 'keydown' && e.which === 27)) {
                        if (e.type === 'keydown' && e.which === 27) {
                            // Esc нажат - отменяем ввод и возвращаем как было
                            cell.text(originalValue);
                        } else {
                            // blur или Enter нажат - сохраняем изменения
                            var newValue = $(this).val();

                            // Отправляем AJAX запрос для сохранения изменений
                            $.ajax({
                                url: '/admin/storage/'+relatedModel+'/' + pk + '/change/',
                                type: 'POST',
                                data: {
                                    csrfmiddlewaretoken: '{{ csrf_token }}',
                                    field: field,
                                    value: newValue
                                },
                                success: function(response) {
                                    if (response.success) {
                                        cell.text(newValue);
                                        showNotification(cell, 'note');
                                    } else {
                                        cell.text(originalValue);
                                        showNotification(cell, 'error');
                                    }
                                },
                                error: function() {
                                    cell.text(originalValue);
                                    showNotification(cell, 'error');
                                }
                            });
                        }
                    }
                });
            }
        }
    });

    // Функция для отображения уведомлений
    function showNotification(cell, type) {
        cell.addClass(type).delay(8000).queue(function(next){
            $(this).removeClass(type);
            next();
        });
    }
});